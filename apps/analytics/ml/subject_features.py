"""
Contrato de features para el modelo por materia (modelo_riesgo_materia).

Cada fila de entrenamiento corresponde a un (enrollment, subject_offering, period)
y predice si ESA materia específica irá a rojo (final_avg_truncated < 7.00).
"""

from decimal import Decimal
from pathlib import Path

from django.conf import settings

SUBJECT_MODEL_DIR = Path(settings.BASE_DIR) / "apps" / "analytics" / "ml" / "subject_models"
SUBJECT_MODEL_DIR.mkdir(parents=True, exist_ok=True)

SUBJECT_FEATURES = [
    "grade_in_subject",
    "grade_trend_in_subject",
    "attendance_in_subject",
    "formative_avg_in_subject",
    "summative_avg_in_subject",
    "prev_period_grade_in_subject",
    "attendance_rate",
    "consecutive_absences_max",
    "tardiness_count",
    "conduct_score",
    "severe_incidents_count",
    "age_grade_gap",
    "is_repeat",
    "has_special_needs",
]

TRAIN_SUBJECT_FEATURES = [f for f in SUBJECT_FEATURES if f != "grade_in_subject"]

SUBJECT_CODES = ["MAT", "FIS", "QUI", "BIO", "LEN", "ING", "SOC", "FIL", "EDU_FIS", "EDU_ART"]


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


def subject_model_path(subject_code):
    return SUBJECT_MODEL_DIR / f"subject_{subject_code.lower()}.joblib"
