"""
Contrato de features para el modelo de riesgo de desercion escolar.

Predice la probabilidad de abandono/no continuidad usando seniales disponibles
antes o durante el periodo academico. Reutiliza el contrato general porque esas
variables ya resumen asistencia, rendimiento, conducta y contexto.
"""

from pathlib import Path

from django.conf import settings

from .features import FEATURE_COLUMNS, _to_number

DROPOUT_MODEL_PATH = (
    Path(settings.BASE_DIR) / "apps" / "analytics" / "ml" / "dropout_risk_model.joblib"
)

DROPOUT_FEATURES = FEATURE_COLUMNS
TRAIN_DROPOUT_FEATURES = DROPOUT_FEATURES

DROPOUT_FEATURE_LABELS = {
    "attendance_rate": "Asistencia general",
    "consecutive_absences_max": "Ausencias consecutivas",
    "tardiness_count": "Tardanzas",
    "justified_absences": "Faltas justificadas",
    "unjustified_absences": "Faltas injustificadas",
    "formative_avg_normalized": "Promedio formativo",
    "summative_avg_normalized": "Promedio sumativo",
    "grade_trend_slope": "Tendencia de notas",
    "failing_subjects_count": "Materias reprobadas",
    "conduct_score": "Conducta",
    "severe_incidents_count": "Incidentes graves",
    "family_notified_ratio": "Notificacion familiar",
    "prev_period_avg_grade": "Nota periodo anterior",
    "age_grade_gap": "Brecha edad-grado",
    "is_repeat": "Repitente",
    "has_special_needs": "Necesidades especiales",
}
