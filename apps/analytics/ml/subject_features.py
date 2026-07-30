"""
Contrato de features para el modelo de riesgo por materia (único).

Cada fila de entrenamiento corresponde a un (enrollment, subject_offering, period)
de CUALQUIER materia. Incluye subject_code_idx para que el modelo
aprenda los patrones específicos de cada materia.

Los códigos se obtienen dinámicamente de la base de datos (cátalogo real)
en lugar de usar listas hardcodeadas.
"""

from decimal import Decimal
from pathlib import Path

from django.conf import settings

SUBJECT_MODEL_PATH = (
    Path(settings.BASE_DIR) / "apps" / "analytics" / "ml" / "subject_risk_model.joblib"
)

SUBJECT_CODES = [
    "MAT",     # Matemática
    "FIS",     # Física
    "QUI",     # Química
    "BIO",     # Biología
    "HIS",     # Historia
    "SOC",     # Historia y CC.SS. (catálogo legacy)
    "CIU",     # Educación para la Ciudadanía
    "FIL",     # Filosofía
    "LEN",     # Lengua y Literatura
    "ING",     # Inglés
    "EA",      # Educación Cultural y Artística
    "EDU_ART", # Educación Cultural y Artística (legacy)
    "EF",      # Educación Física
    "EDU_FIS", # Educación Física (legacy)
    "EMP",     # Emprendimiento y Gestión
    "ACO",     # Acompañamiento Integral
    "CIE",     # Ciencias Naturales (legacy)
    "INF",     # Informática Aplicada
]
SUBJECT_CODE_MAP = {code: idx for idx, code in enumerate(SUBJECT_CODES)}

SUBJECT_FEATURES = [
    "subject_code_idx",
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
