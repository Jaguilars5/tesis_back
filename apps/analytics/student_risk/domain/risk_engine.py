"""
Motor de cálculo de riesgo académico.

Lógica de scoring por reglas y ML extraída de tasks.py.
Proporciona cálculo de riesgo, umbrales y predicciones ML.
"""

import logging
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Optional, Any

from django.conf import settings
from django.utils import timezone

from apps.analytics.ml import features
from apps.analytics.ml.features import FEATURE_COLUMNS, MODEL_PATH

logger = logging.getLogger(__name__)

MODEL_VERSION_FALLBACK = "rules-fallback-v1"
MODEL_VERSION_SKLEARN = "sklearn-joblib-v2"

_model_available = MODEL_PATH.exists()
if _model_available:
    logger.info(
        "[INIT] Modelo ML encontrado en %s. Las predicciones usarán GradientBoosting.",
        MODEL_PATH,
    )
else:
    logger.warning(
        "[INIT] Modelo ML NO encontrado en %s. Todos los cálculos usarán fallback por reglas. "
        "Ejecuta: python manage.py train_risk_model --period-id=X",
        MODEL_PATH,
    )


@dataclass(frozen=True)
class RiskCalculationResult:
    """Resultado del cálculo de riesgo."""

    student_id: str
    period_id: str
    level: str  # rojo, amarillo, verde
    score: float
    model_version: str
    used_ml: bool
    critical_factors: List[str]
    recommendations: List[str]
    detail_by_variable: Dict[str, Any]
    analysis_timestamp: str


def calculate_risk(
    snapshot: Dict,
    metrics: Optional[Dict] = None,
    config=None,
) -> Dict[str, Any]:
    """
    Calcula el semáforo de riesgo.

    Mantiene reglas críticas para la etiqueta y usa
    ML opcional para ajustar el puntaje si existe un artefacto entrenado.
    """
    from .services import RiskScoringConfigService

    if config is None:
        config = RiskScoringConfigService.get_effective_config()

    variables = snapshot["variables"]
    detail = _detail_by_variable(variables, config)
    factors = _critical_factors(variables, config)
    recommendations = _recommendations(factors, variables, config)
    level = _risk_level(variables, config)
    fallback_score = _fallback_risk_score(variables, level, config)

    # El motor ML solo se intenta cuando la institución lo selecciona.
    ml_score = _predict_ml_score(snapshot, metrics) if config.engine == "ML" else None
    score = ml_score if ml_score is not None else fallback_score
    if ml_score is not None:
        model_version = MODEL_VERSION_SKLEARN
    elif config.version_tag:
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


def _public_analysis(analysis: Dict) -> Dict:
    """Versión pública del análisis (sin model_version)."""
    public = analysis.copy()
    public.pop("model_version", None)
    return public


def _risk_level(variables: Dict, config) -> str:
    """Determina el nivel de riesgo basado en umbrales."""
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


def _detail_by_variable(variables: Dict, config) -> Dict:
    """Detalle por variable de riesgo."""
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


def _conduct_level(conducta: Dict, config) -> str:
    """Nivel de riesgo para conducta."""
    if conducta["faltas_graves"] > config.severe_red_min:
        return "rojo"
    if (
        conducta["faltas_leves"] > config.mild_yellow_min
        or conducta["faltas_graves"] > 0
    ):
        return "amarillo"
    return "verde"


def _attendance_level(asistencia: Dict, config) -> str:
    """Nivel de riesgo para asistencia."""
    attendance = asistencia["porcentaje_asistencia"]
    if attendance < config.attendance_red_max:
        return "rojo"
    if attendance <= config.attendance_yellow_max:
        return "amarillo"
    return "verde"


def _grades_level(calificaciones: Dict, config) -> str:
    """Nivel de riesgo para calificaciones."""
    average = calificaciones["promedio_actual"]
    if average < config.average_red_max:
        return "rojo"
    if average <= config.average_yellow_max:
        return "amarillo"
    return "verde"


def _critical_factors(variables: Dict, config) -> List[str]:
    """Factores críticos identificados."""
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


def _recommendations(factors: List[str], variables: Dict, config) -> List[str]:
    """Recomendaciones basadas en factores."""
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
        recommendations.append(
            "Dar seguimiento conductual con docente tutor o DECE"
        )
    if not recommendations:
        recommendations.append("Mantener seguimiento preventivo regular")
    return recommendations


def _fallback_risk_score(variables: Dict, level: str, config) -> float:
    """Score de riesgo por reglas (fallback)."""
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


def _predict_ml_score(snapshot: Dict, metrics: Optional[Dict] = None) -> Optional[float]:
    """
    Predicción ML. Retorna score o None para fallback por reglas.
    """
    estudiante_id = snapshot.get("estudiante_id", "?")

    if not MODEL_PATH.exists():
        logger.info(
            "[ML][FALLBACK-INTENCIONAL] Estudiante=%s — No existe artefacto en %s. "
            "Se usa el motor de reglas. Entrena con: python manage.py train_risk_model",
            estudiante_id,
            MODEL_PATH,
        )
        return None

    try:
        import joblib

        logger.info(
            "[ML] Estudiante=%s — Cargando modelo desde %s",
            estudiante_id,
            MODEL_PATH,
        )
        model = joblib.load(MODEL_PATH)
    except ImportError as exc:
        logger.exception(
            "[ML][ERROR] Estudiante=%s — Dependencia ausente al cargar el modelo (%s). Fallback.",
            estudiante_id,
            exc,
        )
        return None
    except Exception:
        logger.exception(
            "[ML][ERROR] Estudiante=%s — No se pudo cargar el artefacto del modelo. Fallback.",
            estudiante_id,
        )
        return None

    # Validación explícita del contrato de columnas
    model_columns = getattr(model, "feature_names_in_", None)
    if model_columns is not None and not features.columns_match(model_columns):
        logger.warning(
            "[ML][FALLBACK-INTENCIONAL] Estudiante=%s — Desajuste de columnas tren/inferencia. "
            "modelo=%s contrato=%s. Se usa el motor de reglas.",
            estudiante_id,
            list(model_columns),
            FEATURE_COLUMNS,
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
                estudiante_id,
                score,
            )
            return score

        prediction = model.predict(prediction_input)[0]
        if isinstance(prediction, str):
            score = _score_for_label(prediction)
            logger.info(
                "[ML] Estudiante=%s — predict etiqueta='%s' score=%.2f",
                estudiante_id,
                prediction,
                score,
            )
            return score

        score = max(0, min(100, float(prediction)))
        logger.info(
            "[ML] Estudiante=%s — predict numerico=%.2f score=%.2f",
            estudiante_id,
            float(prediction),
            score,
        )
        return score
    except Exception:
        logger.exception(
            "[ML][ERROR] Estudiante=%s — Excepcion inesperada al predecir. Fallback.",
            estudiante_id,
        )
        return None


def _prediction_input(feature_dict: Dict):
    """Convierte feature dict a formato de entrada para el modelo."""
    try:
        import pandas as pd

        return pd.DataFrame([feature_dict], columns=FEATURE_COLUMNS)
    except Exception:
        return [features.feature_row(feature_dict)]


def _score_from_proba(model, prediction_input) -> float:
    """Extrae score de probabilidades del modelo."""
    probabilities = model.predict_proba(prediction_input)[0]
    classes = [str(item).lower() for item in getattr(model, "classes_", [])]
    if "rojo" in classes:
        return float(probabilities[classes.index("rojo")]) * 100
    if "alto" in classes:
        return float(probabilities[classes.index("alto")]) * 100
    return float(max(probabilities)) * 100


def _score_for_label(label: str) -> float:
    """Score asignado a etiquetas categóricas."""
    normalized = label.lower()
    if normalized in ("rojo", "alto"):
        return 85
    if normalized in ("amarillo", "medio", "moderado"):
        return 55
    return 20


def _feature_vector(snapshot: Dict, metrics: Optional[Dict] = None) -> Dict:
    """Vector de features para el modelo."""
    if metrics:
        return features.feature_dict_from_metrics(metrics)
    return features.feature_dict_from_snapshot(snapshot)
