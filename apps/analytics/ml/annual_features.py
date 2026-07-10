"""
Contrato de features para el modelo anual (modelo_riesgo_anual).

Predice si el estudiante perderá el año (1+ materia con annual_final_avg < 7.00)
usando datos disponibles en un período intermedio del año escolar.

Cada fila de entrenamiento corresponde a un (enrollment, academic_period)
y el target es AnnualGradeSummary.is_failing para el año completo.
"""

from decimal import Decimal
from pathlib import Path

from django.conf import settings

ANNUAL_MODEL_PATH = (
    Path(settings.BASE_DIR) / "apps" / "analytics" / "ml" / "annual_risk_model.joblib"
)

ANNUAL_FEATURES = [
    "period_index",
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

TRAIN_ANNUAL_FEATURES = [
    f for f in ANNUAL_FEATURES if f != "failing_subjects_count"
]


def _to_number(value):
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
