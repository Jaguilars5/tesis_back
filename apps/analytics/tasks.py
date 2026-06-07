"""
Celery tasks para calculo asincrono de riesgo academico.
"""

import logging
from pathlib import Path

from celery import shared_task
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.analytics.repositories import (
    StudentFeatureSnapshotRepository,
    StudentRiskScoreRepository,
)
from apps.analytics.services.feature_builder import AcademicRiskFeatureBuilder


logger = logging.getLogger(__name__)

MODEL_VERSION_FALLBACK = "rules-fallback-v1"
MODEL_VERSION_SKLEARN = "sklearn-joblib-v1"
MODEL_PATH = Path(settings.BASE_DIR) / "apps" / "analytics" / "ml" / "risk_model.joblib"

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

        analysis = calculate_academic_risk(snapshot)
        metrics = builder.build_persistence_metrics(snapshot)

        with transaction.atomic():
            StudentFeatureSnapshotRepository.create_snapshot(
                student_id=student_id,
                academic_period_id=academic_period_id,
                metrics=metrics,
            )
            StudentRiskScoreRepository.create_score(
                student_id=student_id,
                academic_period_id=academic_period_id,
                risk_score=analysis["semaforo_riesgo"]["puntaje_riesgo"],
                risk_label=analysis["semaforo_riesgo"]["nivel"],
                model_version=analysis["model_version"],
            )

        logger.info(
            "Riesgo academico persistido student_id=%s academic_period_id=%s task_id=%s",
            student_id,
            academic_period_id,
            task_id,
        )
        return _public_analysis(analysis)
    except ValueError:
        logger.exception(
            "Error de validacion en riesgo academico student_id=%s academic_period_id=%s task_id=%s",
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


def calculate_academic_risk(snapshot):
    """
    Calcula el semaforo de riesgo. Mantiene reglas criticas para la etiqueta y usa
    ML opcional para ajustar el puntaje si existe un artefacto entrenado.
    """
    variables = snapshot["variables"]
    detail = _detail_by_variable(variables)
    factors = _critical_factors(variables)
    recommendations = _recommendations(factors, variables)
    level = _risk_level(variables)
    fallback_score = _fallback_risk_score(variables, level)
    ml_score = _predict_ml_score(snapshot)
    score = ml_score if ml_score is not None else fallback_score
    model_version = MODEL_VERSION_SKLEARN if ml_score is not None else MODEL_VERSION_FALLBACK

    return {
        "estudiante_id": snapshot["estudiante_id"],
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


def _risk_level(variables):
    conducta = variables["conducta"]
    asistencia = variables["asistencia"]
    calificaciones = variables["calificaciones"]

    attendance = asistencia["porcentaje_asistencia"]
    average = calificaciones["promedio_actual"]
    severe = conducta["faltas_graves"]
    mild = conducta["faltas_leves"]

    if attendance < 70 or average < 6.0 or severe > 3:
        return "rojo"
    if 70 <= attendance <= 85 or 6.0 <= average <= 7.0 or mild > 5:
        return "amarillo"
    return "verde"


def _detail_by_variable(variables):
    return {
        "conducta": {
            "nivel": _conduct_level(variables["conducta"]),
            "peso": WEIGHTS["conducta"],
        },
        "asistencia": {
            "nivel": _attendance_level(variables["asistencia"]),
            "peso": WEIGHTS["asistencia"],
        },
        "calificaciones": {
            "nivel": _grades_level(variables["calificaciones"]),
            "peso": WEIGHTS["calificaciones"],
        },
    }


def _conduct_level(conducta):
    if conducta["faltas_graves"] > 3:
        return "rojo"
    if conducta["faltas_leves"] > 5 or conducta["faltas_graves"] > 0:
        return "amarillo"
    return "verde"


def _attendance_level(asistencia):
    attendance = asistencia["porcentaje_asistencia"]
    if attendance < 70:
        return "rojo"
    if attendance <= 85:
        return "amarillo"
    return "verde"


def _grades_level(calificaciones):
    average = calificaciones["promedio_actual"]
    if average < 6.0:
        return "rojo"
    if average <= 7.0:
        return "amarillo"
    return "verde"


def _critical_factors(variables):
    factors = []
    conducta = variables["conducta"]
    asistencia = variables["asistencia"]
    calificaciones = variables["calificaciones"]

    if asistencia["total_registros"] == 0:
        factors.append("Sin registros de asistencia")
    if calificaciones["total_calificaciones"] == 0:
        factors.append("Sin registros de calificaciones")
    if asistencia["porcentaje_asistencia"] < 70:
        factors.append("Asistencia menor al 70%")
    if 70 <= asistencia["porcentaje_asistencia"] <= 85:
        factors.append("Asistencia entre 70% y 85%")
    if calificaciones["promedio_actual"] < 6.0:
        factors.append("Promedio academico menor a 6.0")
    if 6.0 <= calificaciones["promedio_actual"] <= 7.0:
        factors.append("Promedio academico entre 6.0 y 7.0")
    if conducta["faltas_graves"] > 3:
        factors.append("Mas de 3 faltas graves")
    if conducta["faltas_leves"] > 5:
        factors.append("Mas de 5 faltas leves")
    if calificaciones["materias_reprobadas"] > 0:
        factors.append("Materias reprobadas detectadas")
    return factors


def _recommendations(factors, variables):
    recommendations = []
    if "Sin registros de asistencia" in factors:
        recommendations.append("Registrar asistencia del periodo para mejorar el analisis")
    if "Sin registros de calificaciones" in factors:
        recommendations.append("Registrar calificaciones del periodo para mejorar el analisis")
    if variables["asistencia"]["porcentaje_asistencia"] < 85:
        recommendations.append("Revisar plan de asistencia y contactar al representante")
    if variables["calificaciones"]["promedio_actual"] <= 7.0:
        recommendations.append("Planificar refuerzo academico en materias con bajo rendimiento")
    if variables["conducta"]["faltas_leves"] > 5 or variables["conducta"]["faltas_graves"] > 0:
        recommendations.append("Dar seguimiento conductual con docente tutor o DECE")
    if not recommendations:
        recommendations.append("Mantener seguimiento preventivo regular")
    return recommendations


def _fallback_risk_score(variables, level):
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
        conduct_risk * WEIGHTS["conducta"]
        + attendance_risk * WEIGHTS["asistencia"]
        + grades_risk * WEIGHTS["calificaciones"]
    )

    if level == "rojo":
        score = max(score, 70)
    elif level == "amarillo":
        score = max(score, 40)
    else:
        score = min(score, 39.99)
    return max(0, min(100, score))


def _predict_ml_score(snapshot):
    if not MODEL_PATH.exists():
        logger.warning("Modelo ML no encontrado en %s; usando fallback", MODEL_PATH)
        return None

    try:
        import joblib

        model = joblib.load(MODEL_PATH)
        features = _feature_vector(snapshot)
        prediction_input = _prediction_input(features)

        if hasattr(model, "predict_proba"):
            return _score_from_proba(model, prediction_input)

        prediction = model.predict(prediction_input)[0]
        if isinstance(prediction, str):
            return _score_for_label(prediction)
        return max(0, min(100, float(prediction)))
    except Exception:
        logger.exception("No se pudo aplicar modelo ML; usando fallback")
        return None


def _prediction_input(features):
    try:
        import pandas as pd

        return pd.DataFrame([features])
    except Exception:
        return [list(features.values())]


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
def batch_calculate_academic_risk(self, academic_period_id, student_ids):
    total = len(student_ids)
    results = {"total": total, "processed": 0, "failed": 0, "errors": []}

    for student_id in student_ids:
        try:
            calculate_student_academic_risk_task(student_id, academic_period_id)
            results["processed"] += 1
        except Exception as exc:
            results["failed"] += 1
            results["errors"].append({"student_id": student_id, "error": str(exc)})
            logger.error("Error calculando riesgo para estudiante %s: %s", student_id, exc)

    logger.info(
        "Batch risk calculation completed: %d/%d processed, %d failed (task_id=%s)",
        results["processed"], total, results["failed"], getattr(self.request, "id", None),
    )
    return results


def _feature_vector(snapshot):
    variables = snapshot["variables"]
    conducta = variables["conducta"]
    asistencia = variables["asistencia"]
    calificaciones = variables["calificaciones"]
    return {
        "faltas_leves": conducta["faltas_leves"],
        "faltas_graves": conducta["faltas_graves"],
        "porcentaje_asistencia": asistencia["porcentaje_asistencia"],
        "total_faltas": asistencia["total_faltas"],
        "faltas_injustificadas": asistencia["faltas_injustificadas"],
        "promedio_actual": calificaciones["promedio_actual"],
        "materias_reprobadas": calificaciones["materias_reprobadas"],
        "ultimo_examen": calificaciones["ultimo_examen"],
    }
