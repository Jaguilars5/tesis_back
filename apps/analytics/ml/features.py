"""
Contrato único de features para el modelo de riesgo académico (Fase 1).

Este módulo es la **única fuente de verdad** de las columnas de features. Tanto el
entrenamiento (`apps/analytics/ml/train_model.py`) como la inferencia
(`apps/analytics/tasks._predict_ml_score`) deben consumir EXACTAMENTE las mismas
columnas, en el mismo orden y con los mismos nombres.

Cualquier divergencia entre tren e inferencia rompe el scoring del modelo
(scikit-learn lanza *feature names mismatch*) y debe ser detectada por los tests
de contrato (`apps/analytics/tests/test_phase1_feature_contract.py`).
"""

from decimal import Decimal
from pathlib import Path

from django.conf import settings

# Ruta canónica del artefacto entrenado. Centralizada aquí para que entrenamiento
# (train_model) e inferencia (tasks) usen la MISMA ubicación.
MODEL_PATH = Path(settings.BASE_DIR) / "apps" / "analytics" / "ml" / "risk_model.joblib"

# Orden canónico de features. Coincide con los campos de StudentFeatureSnapshot
# usados en entrenamiento. NO reordenar/renombrar sin reentrenar el modelo
# (y bumpear MODEL_VERSION_SKLEARN).
FEATURE_COLUMNS = [
    "attendance_rate",
    "consecutive_absences_max",
    "tardiness_count",
    "justified_absences",
    "unjustified_absences",
    "formative_avg_normalized",
    "summative_avg_normalized",
    "grade_trend_slope",
    "failing_subjects_count",
    "conduct_score",
    "severe_incidents_count",
    "family_notified_ratio",
    "prev_period_avg_grade",
    "age_grade_gap",
    "is_repeat",
    "has_special_needs",
]

# Features para entrenamiento supervisado: excluye failing_subjects_count
# porque tiene correlación directa (leakage) con el target is_failing:
# si count > 0 → is_failing = True siempre.
TRAIN_FEATURES = [col for col in FEATURE_COLUMNS if col != "failing_subjects_count"]

CONDUCT_BASE = 10.0


def _to_number(value):
    """Normaliza cualquier valor a float apto para scikit-learn."""
    if value is None:
        return 0.0
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, Decimal):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def conduct_score_from_counts(leves, moderadas, graves):
    """Réplica del cálculo de conduct_score de feature_builder, para construir el
    feature desde el snapshot crudo cuando no hay métricas persistidas."""
    penalty = (leves or 0) * 0.5 + (moderadas or 0) * 1.0 + (graves or 0) * 2.0
    return max(0.0, min(CONDUCT_BASE, CONDUCT_BASE - penalty))


def _ordered(raw):
    """Devuelve un dict ordenado y numérico siguiendo FEATURE_COLUMNS."""
    return {col: _to_number(raw.get(col)) for col in FEATURE_COLUMNS}


def feature_dict_from_metrics(metrics):
    """
    Mapea el dict de métricas de persistencia (salida de
    `AcademicRiskFeatureBuilder.build_persistence_metrics`) al contrato canónico.

    Refleja el mismo mapeo que usa el repositorio al persistir el
    StudentFeatureSnapshot (`avg_grade_normalized` → formativo + sumativo).
    """
    metrics = metrics or {}
    avg = metrics.get("avg_grade_normalized")
    raw = {
        "attendance_rate": metrics.get("attendance_rate"),
        "consecutive_absences_max": metrics.get("consecutive_absences_max"),
        "tardiness_count": metrics.get("tardiness_count"),
        "justified_absences": metrics.get("justified_absences"),
        "unjustified_absences": metrics.get("unjustified_absences"),
        "formative_avg_normalized": metrics.get("formative_avg_normalized", avg),
        "summative_avg_normalized": metrics.get("summative_avg_normalized", avg),
        "grade_trend_slope": metrics.get("grade_trend_slope"),
        "failing_subjects_count": metrics.get("failing_subjects_count"),
        "conduct_score": metrics.get("conduct_score"),
        "severe_incidents_count": metrics.get("severe_incidents_count"),
        "family_notified_ratio": metrics.get("family_notified_ratio"),
        "prev_period_avg_grade": metrics.get("prev_period_avg_grade"),
        "age_grade_gap": metrics.get("age_grade_gap"),
        "is_repeat": metrics.get("is_repeat"),
        "has_special_needs": metrics.get("has_special_needs"),
    }
    return _ordered(raw)


def feature_dict_from_snapshot(snapshot, metrics=None):
    """
    Construye el contrato canónico a partir del snapshot crudo (`variables`).

    Si se proporcionan `metrics`, los campos derivados de BD (promedio del periodo
    previo, brecha edad-grado, repitente, NEE y conduct_score) se toman de ellas
    para mayor fidelidad con el snapshot persistido/entrenado.
    """
    variables = snapshot.get("variables", {})
    conducta = variables.get("conducta", {})
    asistencia = variables.get("asistencia", {})
    calificaciones = variables.get("calificaciones", {})

    avg = calificaciones.get("promedio_actual")
    raw = {
        "attendance_rate": asistencia.get("porcentaje_asistencia"),
        "consecutive_absences_max": asistencia.get("max_faltas_consecutivas"),
        "tardiness_count": asistencia.get("tardanzas"),
        "justified_absences": asistencia.get("faltas_justificadas"),
        "unjustified_absences": asistencia.get("faltas_injustificadas"),
        "formative_avg_normalized": avg,
        "summative_avg_normalized": avg,
        "grade_trend_slope": calificaciones.get("tendencia_notas"),
        "failing_subjects_count": calificaciones.get("materias_reprobadas"),
        "conduct_score": conduct_score_from_counts(
            conducta.get("faltas_leves"),
            conducta.get("faltas_moderadas"),
            conducta.get("faltas_graves"),
        ),
        "severe_incidents_count": conducta.get("faltas_graves"),
        "family_notified_ratio": conducta.get("ratio_notificacion_familiar"),
        "prev_period_avg_grade": 0,
        "age_grade_gap": 0,
        "is_repeat": False,
        "has_special_needs": False,
    }

    if metrics:
        if metrics.get("conduct_score") is not None:
            raw["conduct_score"] = metrics["conduct_score"]
        for db_field in (
            "prev_period_avg_grade",
            "age_grade_gap",
            "is_repeat",
            "has_special_needs",
        ):
            if metrics.get(db_field) is not None:
                raw[db_field] = metrics[db_field]

    return _ordered(raw)


def feature_row(feature_dict):
    """Lista ordenada de valores según FEATURE_COLUMNS (fallback sin pandas)."""
    return [feature_dict[col] for col in FEATURE_COLUMNS]


def columns_match(model_columns):
    """
    True si las columnas del modelo coinciden (como conjunto) con el contrato
    canónico. Se usa antes de `predict` para evitar el mismatch silencioso que
    históricamente forzaba el fallback por excepción.
    """
    return set(model_columns) == set(FEATURE_COLUMNS)
