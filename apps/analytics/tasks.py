"""
Celery tasks para calculo asincrono de riesgo academico.
"""

import logging

from celery import shared_task
from django.db import transaction
from django.utils import timezone

from apps.analytics.ml import features
from apps.analytics.ml.features import FEATURE_COLUMNS, MODEL_PATH
from apps.analytics.repositories import (
    StudentFeatureSnapshotRepository,
    StudentRiskScoreRepository,
)
from apps.analytics.services.feature_builder import AcademicRiskFeatureBuilder
from apps.analytics.services.risk_scoring_config_service import (
    DEFAULT_CONFIG,
    RiskScoringConfigService,
)

logger = logging.getLogger(__name__)

MODEL_VERSION_FALLBACK = "rules-fallback-v1"
# v2: contrato de features unificado tren/inferencia (Fase 1). El artefacto debe
# reentrenarse con `python manage.py train_risk_model` tras este cambio.
MODEL_VERSION_SKLEARN = "sklearn-joblib-v2"

_model_available = MODEL_PATH.exists()
if _model_available:
    logger.info(
        "[INIT] Modelo ML encontrado en %s. Las predicciones usaran GradientBoosting.",
        MODEL_PATH,
    )
else:
    logger.warning(
        "[INIT] Modelo ML NO encontrado en %s. Todos los calculos usaran fallback por reglas. "
        "Ejecuta: python manage.py train_risk_model --period-id=X",
        MODEL_PATH,
    )

# Pesos por defecto (replicados en risk_scoring_config_service.DEFAULT_CONFIG).
# Se conservan como constante para compatibilidad/baseline; el cálculo productivo
# usa la configuración efectiva (BD o defaults), ver `calculate_academic_risk`.
WEIGHTS = {
    "conducta": 0.30,
    "asistencia": 0.35,
    "calificaciones": 0.35,
}


@shared_task(bind=True)
def calculate_student_academic_risk_task(self, student_id, academic_period_id):
    """
    Construye snapshot, calcula riesgo academico, persiste resultado y retorna JSON.
    """
    task_id = getattr(self.request, "id", None)
    logger.info(
        "Iniciando calculo de riesgo academico student_id=%s academic_period_id=%s task_id=%s",
        student_id,
        academic_period_id,
        task_id,
    )

    try:
        builder = AcademicRiskFeatureBuilder(student_id, academic_period_id)
        snapshot = builder.build()
        logger.info(
            "Snapshot de riesgo construido student_id=%s academic_period_id=%s task_id=%s",
            student_id,
            academic_period_id,
            task_id,
        )

        metrics = builder.build_persistence_metrics(snapshot)
        analysis = calculate_academic_risk(snapshot, metrics)

        with transaction.atomic():
            StudentFeatureSnapshotRepository.create_snapshot(
                student_id=student_id,
                academic_period_id=academic_period_id,
                metrics=metrics,
            )
            risk_score = StudentRiskScoreRepository.create_score(
                student_id=student_id,
                academic_period_id=academic_period_id,
                risk_score=analysis["semaforo_riesgo"]["puntaje_riesgo"],
                risk_label=analysis["semaforo_riesgo"]["nivel"],
                model_version=analysis["model_version"],
            )

            _populate_risk_factors(risk_score, analysis)

        logger.info(
            "Riesgo academico persistido student_id=%s academic_period_id=%s modelo=%s nivel=%s score=%.2f task_id=%s",
            student_id,
            academic_period_id,
            analysis["model_version"],
            analysis["semaforo_riesgo"]["nivel"],
            analysis["semaforo_riesgo"]["puntaje_riesgo"],
            task_id,
        )
        return _public_analysis(analysis)
    except ValueError:
        logger.exception(
            "Error de validación en riesgo academico student_id=%s academic_period_id=%s task_id=%s",
            student_id,
            academic_period_id,
            task_id,
        )
        raise
    except Exception:
        logger.exception(
            "Error inesperado en riesgo academico student_id=%s academic_period_id=%s task_id=%s",
            student_id,
            academic_period_id,
            task_id,
        )
        raise


def calculate_academic_risk(snapshot, metrics=None):
    """
    Calcula el semaforo de riesgo. Mantiene reglas criticas para la etiqueta y usa
    ML opcional para ajustar el puntaje si existe un artefacto entrenado.

    `metrics` es el dict de metricas de persistencia (build_persistence_metrics).
    Cuando se proporciona, la inferencia ML usa el contrato canonico completo
    (incluye campos derivados de BD: periodo previo, brecha edad-grado, etc.).

    La configuracion efectiva (pesos + umbrales + motor) se lee de
    `RiskScoringConfigService` (Fase 5). Si no hay fila en BD, usa los defaults
    seguros (identicos al comportamiento historico). Con `engine=ML` los
    pesos/umbrales del motor de reglas no afectan el score (el ML aprende los
    suyos); igualmente se cae al fallback por reglas si no hay artefacto.
    """
    config = RiskScoringConfigService.get_effective()

    variables = snapshot["variables"]
    detail = _detail_by_variable(variables, config)
    factors = _critical_factors(variables, config)
    recommendations = _recommendations(factors, variables, config)
    level = _risk_level(variables, config)
    fallback_score = _fallback_risk_score(variables, level, config)

    # El motor ML solo se intenta cuando la institucion lo selecciona.
    ml_score = _predict_ml_score(snapshot, metrics) if config.engine == "ML" else None
    score = ml_score if ml_score is not None else fallback_score
    if ml_score is not None:
        model_version = MODEL_VERSION_SKLEARN
    elif config.version_tag:
        # Refleja la config aplicada en el motor de reglas (trazabilidad/tesis).
        model_version = f"{MODEL_VERSION_FALLBACK}+{config.version_tag}"
    else:
        model_version = MODEL_VERSION_FALLBACK

    estudiante_id = snapshot["estudiante_id"]
    logger.info(
        "Riesgo calculado estudiante=%s nivel=%s puntaje=%.2f modelo=%s ml=%s fallback=%.2f",
        estudiante_id,
        level,
        round(float(score), 2),
        model_version,
        "SI" if ml_score is not None else "NO",
        round(float(fallback_score), 2),
    )

    return {
        "estudiante_id": estudiante_id,
        "periodo": snapshot["periodo"],
        "fecha_analisis": timezone.now().isoformat(),
        "semaforo_riesgo": {
            "nivel": level,
            "puntaje_riesgo": round(float(score), 2),
            "factores_criticos": factors,
            "recomendaciones": recommendations,
        },
        "detalle_por_variable": detail,
        "model_version": model_version,
    }


def _public_analysis(analysis):
    public = analysis.copy()
    public.pop("model_version", None)
    return public


def _risk_level(variables, config=None):
    config = config or DEFAULT_CONFIG
    conducta = variables["conducta"]
    asistencia = variables["asistencia"]
    calificaciones = variables["calificaciones"]

    attendance = asistencia["porcentaje_asistencia"]
    average = calificaciones["promedio_actual"]
    severe = conducta["faltas_graves"]
    mild = conducta["faltas_leves"]

    if (
        attendance < config.attendance_red_max
        or average < config.average_red_max
        or severe > config.severe_red_min
    ):
        return "rojo"
    if (
        config.attendance_red_max <= attendance <= config.attendance_yellow_max
        or config.average_red_max <= average <= config.average_yellow_max
        or mild > config.mild_yellow_min
    ):
        return "amarillo"
    return "verde"


def _detail_by_variable(variables, config=None):
    config = config or DEFAULT_CONFIG
    weights = config.weights
    return {
        "conducta": {
            "nivel": _conduct_level(variables["conducta"], config),
            "peso": weights["conducta"],
        },
        "asistencia": {
            "nivel": _attendance_level(variables["asistencia"], config),
            "peso": weights["asistencia"],
        },
        "calificaciones": {
            "nivel": _grades_level(variables["calificaciones"], config),
            "peso": weights["calificaciones"],
        },
    }


def _conduct_level(conducta, config=None):
    config = config or DEFAULT_CONFIG
    if conducta["faltas_graves"] > config.severe_red_min:
        return "rojo"
    if conducta["faltas_leves"] > config.mild_yellow_min or conducta["faltas_graves"] > 0:
        return "amarillo"
    return "verde"


def _attendance_level(asistencia, config=None):
    config = config or DEFAULT_CONFIG
    attendance = asistencia["porcentaje_asistencia"]
    if attendance < config.attendance_red_max:
        return "rojo"
    if attendance <= config.attendance_yellow_max:
        return "amarillo"
    return "verde"


def _grades_level(calificaciones, config=None):
    config = config or DEFAULT_CONFIG
    average = calificaciones["promedio_actual"]
    if average < config.average_red_max:
        return "rojo"
    if average <= config.average_yellow_max:
        return "amarillo"
    return "verde"


def _critical_factors(variables, config=None):
    config = config or DEFAULT_CONFIG
    factors = []
    conducta = variables["conducta"]
    asistencia = variables["asistencia"]
    calificaciones = variables["calificaciones"]
    attendance = asistencia["porcentaje_asistencia"]
    average = calificaciones["promedio_actual"]

    if asistencia["total_registros"] == 0:
        factors.append("Sin registros de asistencia")
    if calificaciones["total_calificaciones"] == 0:
        factors.append("Sin registros de calificaciones")
    if attendance < config.attendance_red_max:
        factors.append("Asistencia en nivel critico (rojo)")
    elif attendance <= config.attendance_yellow_max:
        factors.append("Asistencia en nivel de alerta (amarillo)")
    if average < config.average_red_max:
        factors.append("Promedio academico en nivel critico (rojo)")
    elif average <= config.average_yellow_max:
        factors.append("Promedio academico en nivel de alerta (amarillo)")
    if conducta["faltas_graves"] > config.severe_red_min:
        factors.append("Faltas graves por encima del umbral configurado")
    if conducta["faltas_leves"] > config.mild_yellow_min:
        factors.append("Faltas leves por encima del umbral configurado")
    if calificaciones["materias_reprobadas"] > 0:
        factors.append("Materias reprobadas detectadas")
    return factors


def _recommendations(factors, variables, config=None):
    config = config or DEFAULT_CONFIG
    recommendations = []
    if "Sin registros de asistencia" in factors:
        recommendations.append(
            "Registrar asistencia del periodo para mejorar el analisis"
        )
    if "Sin registros de calificaciones" in factors:
        recommendations.append(
            "Registrar calificaciones del periodo para mejorar el analisis"
        )
    if variables["asistencia"]["porcentaje_asistencia"] <= config.attendance_yellow_max:
        recommendations.append(
            "Revisar plan de asistencia y contactar al representante"
        )
    if variables["calificaciones"]["promedio_actual"] <= config.average_yellow_max:
        recommendations.append(
            "Planificar refuerzo academico en materias con bajo rendimiento"
        )
    if (
        variables["conducta"]["faltas_leves"] > config.mild_yellow_min
        or variables["conducta"]["faltas_graves"] > 0
    ):
        recommendations.append("Dar seguimiento conductual con docente tutor o DECE")
    if not recommendations:
        recommendations.append("Mantener seguimiento preventivo regular")
    return recommendations


def _fallback_risk_score(variables, level, config=None):
    config = config or DEFAULT_CONFIG
    weights = config.weights
    conducta = variables["conducta"]
    asistencia = variables["asistencia"]
    calificaciones = variables["calificaciones"]

    conduct_risk = min(
        100,
        conducta["faltas_leves"] * 5
        + conducta.get("faltas_moderadas", 0) * 10
        + conducta["faltas_graves"] * 25,
    )
    attendance_risk = 100 - asistencia["porcentaje_asistencia"]
    grades_risk = min(
        100,
        ((10 - calificaciones["promedio_actual"]) / 10 * 100)
        + calificaciones["materias_reprobadas"] * 15,
    )

    score = (
        conduct_risk * weights["conducta"]
        + attendance_risk * weights["asistencia"]
        + grades_risk * weights["calificaciones"]
    )

    if level == "rojo":
        score = max(score, 70)
    elif level == "amarillo":
        score = max(score, 40)
    else:
        score = min(score, 39.99)
    return max(0, min(100, score))


def _predict_ml_score(snapshot, metrics=None):
    """
    Devuelve el score del modelo ML, o None para caer al fallback por reglas.

    El None se distingue por intencion en los logs:
    - "[ML][FALLBACK-INTENCIONAL]": el modelo no esta, o sus columnas no coinciden
      con el contrato canonico (no es un error: es la decision de no puntuar con ML).
    - "[ML][ERROR]": excepcion inesperada durante la carga/prediccion.
    """
    estudiante_id = snapshot.get("estudiante_id", "?")

    if not MODEL_PATH.exists():
        logger.info(
            "[ML][FALLBACK-INTENCIONAL] Estudiante=%s — No existe artefacto en %s. "
            "Se usa el motor de reglas. Entrena con: python manage.py train_risk_model",
            estudiante_id, MODEL_PATH,
        )
        return None

    try:
        import joblib

        logger.info("[ML] Estudiante=%s — Cargando modelo desde %s", estudiante_id, MODEL_PATH)
        model = joblib.load(MODEL_PATH)
    except ImportError as exc:
        logger.exception(
            "[ML][ERROR] Estudiante=%s — Dependencia ausente al cargar el modelo (%s). Fallback.",
            estudiante_id, exc,
        )
        return None
    except Exception:
        logger.exception(
            "[ML][ERROR] Estudiante=%s — No se pudo cargar el artefacto del modelo. Fallback.",
            estudiante_id,
        )
        return None

    # Validacion explicita del contrato de columnas ANTES de predecir. Si el modelo
    # fue entrenado con otras columnas, NO intentamos predecir (evita el mismatch
    # silencioso que historicamente caia al fallback por excepcion).
    model_columns = getattr(model, "feature_names_in_", None)
    if model_columns is not None and not features.columns_match(model_columns):
        logger.warning(
            "[ML][FALLBACK-INTENCIONAL] Estudiante=%s — Desajuste de columnas tren/inferencia. "
            "modelo=%s contrato=%s. Se usa el motor de reglas.",
            estudiante_id, list(model_columns), FEATURE_COLUMNS,
        )
        return None

    try:
        feature_dict = (
            features.feature_dict_from_metrics(metrics)
            if metrics
            else features.feature_dict_from_snapshot(snapshot)
        )
        logger.info(
            "[ML] Estudiante=%s — Features (%d cols): %s",
            estudiante_id,
            len(feature_dict),
            {k: round(v, 2) if isinstance(v, float) else v for k, v in feature_dict.items()},
        )

        prediction_input = _prediction_input(feature_dict)

        if hasattr(model, "predict_proba"):
            score = _score_from_proba(model, prediction_input)
            logger.info(
                "[ML] Estudiante=%s — predict_proba exitoso. Score=%.2f",
                estudiante_id, score,
            )
            return score

        prediction = model.predict(prediction_input)[0]
        if isinstance(prediction, str):
            score = _score_for_label(prediction)
            logger.info(
                "[ML] Estudiante=%s — predict etiqueta='%s' score=%.2f",
                estudiante_id, prediction, score,
            )
            return score

        score = max(0, min(100, float(prediction)))
        logger.info(
            "[ML] Estudiante=%s — predict numerico=%.2f score=%.2f",
            estudiante_id, float(prediction), score,
        )
        return score
    except Exception:
        logger.exception(
            "[ML][ERROR] Estudiante=%s — Excepcion inesperada al predecir. Fallback.",
            estudiante_id,
        )
        return None


def _prediction_input(feature_dict):
    try:
        import pandas as pd

        return pd.DataFrame([feature_dict], columns=FEATURE_COLUMNS)
    except Exception:
        return [features.feature_row(feature_dict)]


def _score_from_proba(model, prediction_input):
    probabilities = model.predict_proba(prediction_input)[0]
    classes = [str(item).lower() for item in getattr(model, "classes_", [])]
    if "rojo" in classes:
        return float(probabilities[classes.index("rojo")]) * 100
    if "alto" in classes:
        return float(probabilities[classes.index("alto")]) * 100
    return float(max(probabilities)) * 100


def _score_for_label(label):
    normalized = label.lower()
    if normalized in ("rojo", "alto"):
        return 85
    if normalized in ("amarillo", "medio", "moderado"):
        return 55
    return 20


@shared_task(bind=True)
def batch_calculate_academic_risk(self, academic_period_id, student_ids, user_id=None):
    total = len(student_ids)
    results = {"total": total, "processed": 0, "failed": 0, "errors": []}

    for student_id in student_ids:
        try:
            calculate_student_academic_risk_task(student_id, academic_period_id)
            results["processed"] += 1
        except Exception as exc:
            results["failed"] += 1
            results["errors"].append({"student_id": student_id, "error": str(exc)})
            logger.error(
                "Error calculando riesgo para estudiante %s: %s", student_id, exc
            )

    logger.info(
        "[BATCH] period_id=%s total=%d procesados=%d fallidos=%d modelo_disponible=%s task_id=%s",
        academic_period_id,
        total,
        results["processed"],
        results["failed"],
        _model_available,
        getattr(self.request, "id", None),
    )

    if user_id:
        _emit_task_completed(getattr(self.request, "id", None), results, user_id)

    return results


def _emit_task_completed(task_id, results, user_id):
    """
    Publica el evento task_completed via Redis usando el protocolo nativo de
    python-socketio (AsyncRedisManager write_only) para garantizar compatibilidad
    con el servidor ASGI.
    """
    try:
        import json
        import uuid
        import redis as redis_lib
        from django.conf import settings

        # Usar el protocolo nativo de python-socketio para mayor compatibilidad.
        # El mensaje debe incluir: method, event, data (lista), binary, namespace,
        # room, skip_sid, callback, host_id — exactamente como hace PubSubManager.emit().
        r = redis_lib.Redis.from_url(settings.SOCKETIO_REDIS_URL)
        message = json.dumps({
            "method": "emit",
            "event": "task_completed",
            "data": [{"task_id": task_id, "result": results}],
            "binary": False,
            "namespace": "/",
            "room": f"user_{user_id}",
            "skip_sid": None,
            "callback": None,
            "host_id": str(uuid.uuid4()),  # ID único para que el servidor no ignore el mensaje
        })
        r.publish("socketio", message)
        r.close()
        logger.info("[SOCKET.IO] Evento task_completed publicado a Redis para user_%s", user_id)
    except Exception:
        logger.warning("[SOCKET.IO] No se pudo publicar evento a Redis", exc_info=True)


def _feature_vector(snapshot, metrics=None):
    """
    Emite EXACTAMENTE las columnas del contrato canonico (FEATURE_COLUMNS), las
    mismas que consume el entrenamiento. Delega en `ml.features` (fuente unica).
    """
    if metrics:
        return features.feature_dict_from_metrics(metrics)
    return features.feature_dict_from_snapshot(snapshot)


def _populate_risk_factors(risk_score, analysis):
    from apps.analytics.repositories.risk_factor_repository import RiskFactorRepository
    from apps.analytics.repositories.student_risk_factor_repository import (
        StudentRiskFactorRepository,
    )

    factor_mapping = {
        "LOW_ATTENDANCE": ("attendance_rate", 0.35),
        "FAILING_GRADES": ("failing_subjects_count", 0.35),
        "BEHAVIOR_ISSUES": ("severe_incidents_count", 0.20),
        "SOCIOEMOTIONAL": ("conduct_score", 0.10),
    }

    for factor_code, (variable_key, default_weight) in factor_mapping.items():
        factor = RiskFactorRepository.get_by_code(factor_code)
        if not factor:
            continue

        StudentRiskFactorRepository.model.objects.update_or_create(
            student_risk_score=risk_score,
            risk_factor=factor,
            defaults={"contribution_weight": default_weight},
        )


from celery import shared_task
from django.db import transaction as db_transaction


@shared_task(bind=True)
def auto_generate_early_alerts(self, period_id=None):
    from ..services.early_alert_service import EarlyAlertService

    if not period_id:
        from apps.academic.models import AcademicPeriod

        period = AcademicPeriod.objects.filter(is_active=True).first()
        if not period:
            return {"error": "No active period found"}
        period_id = period.id

    from apps.students.models import Enrollment

    enrollments = Enrollment.objects.filter(
        enrollment_status="ACT",
    ).select_related("student")

    alerts_created = 0
    for enrollment in enrollments:
        from apps.academic.models import AcademicPeriod

        period = AcademicPeriod.objects.get(pk=period_id)
        service = EarlyAlertService()
        alerts = service.evaluate_student(enrollment, period)
        alerts_created += len(alerts)

    return {"processed": len(enrollments), "alerts_created": alerts_created}


@shared_task(bind=True)
def run_student_clustering(self, period_id=None):
    from ..services.clustering_service import StudentClusteringService

    if not period_id:
        from apps.academic.models import AcademicPeriod

        period = AcademicPeriod.objects.filter(is_active=True).first()
        if not period:
            return {"error": "No active period found"}
        period_id = period.id
    result = StudentClusteringService.cluster_students(period_id)
    return result


@shared_task(bind=True)
def refresh_materialized_views(self):
    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute(
            "REFRESH MATERIALIZED VIEW CONCURRENTLY analytics_section_risk_summary"
        )
    return {"ok": True}
