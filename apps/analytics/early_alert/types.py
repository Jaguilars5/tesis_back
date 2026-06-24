"""
TypedDicts y tipos para el módulo de alertas tempranas.
"""

from typing import TypedDict, Optional


class ValidationErrors(TypedDict, total=False):
    """Errores de validación por campo."""

    enrollment: str
    academic_period: str
    alert_type: str
    urgency_level: str
    non_field_errors: str


class EarlyAlertPayload(TypedDict, total=False):
    """Payload para crear/actualizar una alerta temprana."""

    enrollment_id: int
    academic_period_id: int
    alert_type: Optional[str]
    description: str
    urgency_level: Optional[str]
