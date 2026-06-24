"""
TypedDicts y tipos para el módulo de riesgo estudiantil.
"""

from typing import TypedDict, Optional, List
from decimal import Decimal


class ValidationErrors(TypedDict, total=False):
    """Errores de validación por campo."""

    enrollment: str
    academic_period: str
    risk_score: str
    risk_label: str
    non_field_errors: str


class RiskScorePayload(TypedDict, total=False):
    """Payload para crear/actualizar un puntaje de riesgo."""

    enrollment_id: int
    academic_period_id: int
    risk_score: Decimal
    risk_label: str
    model_version: str


class RiskConfigPayload(TypedDict, total=False):
    """Payload para actualizar configuración de scoring."""

    engine: str
    preset: str
    weight_conducta: Decimal
    weight_asistencia: Decimal
    weight_calificaciones: Decimal
    attendance_red_max: Decimal
    attendance_yellow_max: Decimal
    average_red_max: Decimal
    average_yellow_max: Decimal
    severe_red_min: int
    mild_yellow_min: int
