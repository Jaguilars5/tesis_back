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
from apps.analytics.ml.features import FEATURE_COLUMNS, TRAIN_FEATURES, MODEL_PATH

logger = logging.getLogger(__name__)

MODEL_VERSION_FALLBACK = "rules-fallback-v1"
MODEL_VERSION_SKLEARN = "sklearn-joblib-v2"

# Umbrales del semáforo derivados del puntaje final (0–100).
# Deben coincidir con la interpretación del simulador ML en el frontend.
SCORE_LEVEL_RED_MIN = 70.0
SCORE_LEVEL_YELLOW_MIN = 40.0

_model_available = MODEL_PATH.exists()


def _default_config():
    """Config efectiva por defecto (baseline). Import perezoso para evitar ciclos."""
    from apps.analytics.services.risk_scoring_config_service import DEFAULT_CONFIG

    return DEFAULT_CONFIG
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

    El puntaje (reglas o ML) y la etiqueta del semáforo comparten los mismos
    umbrales: ``>=70`` rojo, ``>=40`` amarillo, ``<40`` verde. Las reglas por
    variable siguen usándose para factores críticos, recomendaciones y detalle.

    `config` puede ser ``None`` (se lee la config efectiva normalizada), una
    instancia de :class:`EffectiveScoringConfig`, o el modelo singleton
    ``RiskScoringConfig`` (se normaliza). El motor siempre trabaja con la
    config efectiva (pesos como fracciones + ``weights``/``version_tag``).
    """
    from apps.analytics.services.risk_scoring_config_service import (
        EffectiveScoringConfig,
        RiskScoringConfigService,
    )

    config = RiskScoringConfigService._normalize_config(config)

    variables = snapshot["variables"]
    detail = _detail_by_variable(variables, config)
    factors = _critical_factors(variables, config)
    recommendations = _recommendations(factors, variables, config)
    rule_level = _risk_level(variables, config)
    fallback_score = _fallback_risk_score(variables, rule_level, config)

    # El motor ML solo se intenta cuando la institución lo selecciona.
    ml_score = _predict_ml_score(snapshot, metrics) if config.engine == "ML" else None
    score = ml_score if ml_score is not None else fallback_score
    level = _score_to_level(score)
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

    result = {
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

    # Incluir importancias del modelo ML para factores de riesgo dinámicos
    if ml_score is not None:
        importances = _get_ml_feature_importances()
        if importances:
            result["ml_feature_importances"] = importances

    return result


def _public_analysis(analysis: Dict) -> Dict:
    """Versión pública del análisis (sin model_version)."""
    public = analysis.copy()
    public.pop("model_version", None)
    return public


def score_to_risk_label(score: float) -> str:
    """Convierte el puntaje 0–100 en etiqueta de semáforo (API pública)."""
    if score >= SCORE_LEVEL_RED_MIN:
        return "rojo"
    if score >= SCORE_LEVEL_YELLOW_MIN:
        return "amarillo"
    return "verde"


def _score_to_level(score: float) -> str:
    """Alias interno de :func:`score_to_risk_label`."""
    return score_to_risk_label(score)


def _risk_level(variables: Dict, config=None) -> str:
    """Nivel por umbrales de variables (conducta/asistencia/notas). Usado en detalle y factores."""
    config = config or _default_config()
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
        config.attendance_red_max <= attendance < config.attendance_green_min
        or config.average_red_max <= average < config.average_green_min
        or mild > config.mild_yellow_min
    ):
        return "amarillo"
    return "verde"


def _detail_by_variable(variables: Dict, config=None) -> Dict:
    """Detalle por variable de riesgo."""
    config = config or _default_config()
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


def _conduct_level(conducta: Dict, config=None) -> str:
    """Nivel de riesgo para conducta."""
    config = config or _default_config()
    graves = conducta["faltas_graves"]
    leves = conducta["faltas_leves"]
    if graves > config.severe_red_min:
        return "rojo"
    if leves <= config.mild_green_max and graves <= config.severe_green_max:
        return "verde"
    if leves > config.mild_yellow_min or graves > config.severe_green_max:
        return "amarillo"
    return "amarillo"


def _attendance_level(asistencia: Dict, config=None) -> str:
    """Nivel de riesgo para asistencia."""
    config = config or _default_config()
    attendance = asistencia["porcentaje_asistencia"]
    if attendance < config.attendance_red_max:
        return "rojo"
    if attendance < config.attendance_green_min:
        return "amarillo"
    return "verde"


def _grades_level(calificaciones: Dict, config=None) -> str:
    """Nivel de riesgo para calificaciones."""
    config = config or _default_config()
    average = calificaciones["promedio_actual"]
    if average < config.average_red_max:
        return "rojo"
    if average < config.average_green_min:
        return "amarillo"
    return "verde"


def _critical_factors(variables: Dict, config=None) -> List[str]:
    """Factores críticos identificados."""
    config = config or _default_config()
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


def _recommendations(factors: List[str], variables: Dict, config=None) -> List[str]:
    """Recomendaciones basadas en factores."""
    config = config or _default_config()
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


def _fallback_risk_score(variables: Dict, level: str, config=None) -> float:
    """Score de riesgo por reglas (fallback)."""
    config = config or _default_config()
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


_cached_artifact = None
_cached_artifact_mtime = None


def _load_artifact_cached():
    """Carga y mantiene en memoria el artefacto (model + scaler). Recarga si cambia en disco."""
    global _cached_artifact, _cached_artifact_mtime
    import os
    import joblib

    if not MODEL_PATH.exists():
        _cached_artifact = None
        _cached_artifact_mtime = None
        return None

    try:
        current_mtime = os.path.getmtime(MODEL_PATH)
        if _cached_artifact is None or _cached_artifact_mtime != current_mtime:
            logger.info("[ML] Cargando artefacto desde %s (mtime=%s)", MODEL_PATH, current_mtime)
            _cached_artifact = joblib.load(MODEL_PATH)
            _cached_artifact_mtime = current_mtime
        return _cached_artifact
    except Exception:
        logger.exception("[ML][ERROR] Error al cargar o deserializar el artefacto.")
        return None


def _get_ml_feature_importances() -> Optional[List[float]]:
    """Carga las feature importances del artifact del modelo."""
    try:
        artifact = _load_artifact_cached()
        if artifact is None:
            return None
        importances = artifact.get("feature_importances")
        return importances if importances else None
    except Exception:
        return None


def _predict_ml_score(snapshot: Dict, metrics: Optional[Dict] = None) -> Optional[float]:
    """
    Predicción del modelo matemático (regresión logística).

    Retorna ``P(is_failing=True) * 100`` como score 0-100, o ``None``
    para que el motor de reglas actúe como fallback.
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
        artifact = _load_artifact_cached()
        if artifact is None:
            return None
    except Exception:
        logger.exception(
            "[ML][ERROR] Estudiante=%s — No se pudo cargar el artefacto del modelo. Fallback.",
            estudiante_id,
        )
        return None

    model = artifact["model"]
    model_features = artifact.get("features", TRAIN_FEATURES)

    try:
        full_dict = (
            features.feature_dict_from_metrics(metrics)
            if metrics
            else features.feature_dict_from_snapshot(snapshot)
        )
        feature_dict = {col: full_dict.get(col, 0.0) for col in model_features}
        logger.info(
            "[ML] Estudiante=%s — Features (%d cols): %s",
            estudiante_id,
            len(feature_dict),
            {k: round(v, 2) if isinstance(v, float) else v for k, v in feature_dict.items()},
        )

        import pandas as pd
        X = pd.DataFrame([feature_dict], columns=model_features)

        proba = model.predict_proba(X)[0]
        clases = getattr(model, "classes_", [0, 1])
        # classes_[1] = clase positiva (is_failing=True)
        pos_idx = list(clases).index(1) if 1 in clases else 1
        score = round(float(proba[pos_idx]) * 100, 2)

        logger.info(
            "[ML] Estudiante=%s — P(is_failing)=%.4f Score=%.2f",
            estudiante_id,
            float(proba[pos_idx]),
            score,
        )
        return score

    except Exception:
        logger.exception(
            "[ML][ERROR] Estudiante=%s — Excepcion inesperada al predecir. Fallback.",
            estudiante_id,
        )
        return None


def _feature_vector(snapshot: Dict, metrics: Optional[Dict] = None) -> Dict:
    """Vector de features para el modelo."""
    if metrics:
        return features.feature_dict_from_metrics(metrics)
    return features.feature_dict_from_snapshot(snapshot)
