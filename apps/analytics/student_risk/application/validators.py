"""
Validaciones de negocio para riesgo estudiantil.

Funciones puras que retornan dict {field: message} si fallan.
"""

from typing import Dict, Optional
from decimal import Decimal

from apps.students.repositories.enrollment_repository import EnrollmentRepository
from apps.academic.academic_period.infrastructure.repositories import (
    AcademicPeriodRepository,
)

from ..infrastructure.repositories import StudentRiskScoreRepository


def validate_enrollment_exists(enrollment_id: int) -> Dict[str, str]:
    """Valida que la matrícula exista."""
    enrollment = EnrollmentRepository.get_by_id(enrollment_id)
    if not enrollment:
        return {"enrollment": f"Matrícula {enrollment_id} no encontrada"}
    return {}


def validate_academic_period_exists(academic_period_id: int) -> Dict[str, str]:
    """Valida que el período académico exista."""
    period = AcademicPeriodRepository.get_by_id(academic_period_id)
    if not period:
        return {"academic_period": f"Período académico {academic_period_id} no encontrado"}
    return {}


def validate_risk_score_range(risk_score: Decimal) -> Dict[str, str]:
    """Valida que el puntaje de riesgo esté en rango válido (0-100)."""
    if risk_score < 0 or risk_score > 100:
        return {"risk_score": "El puntaje de riesgo debe estar entre 0 y 100"}
    return {}


def validate_risk_label(risk_label: str) -> Dict[str, str]:
    """Valida que la etiqueta de riesgo sea válida."""
    valid_labels = ["verde", "amarillo", "rojo"]
    if risk_label not in valid_labels:
        return {"risk_label": f"Etiqueta '{risk_label}' no válida. Opciones: {', '.join(valid_labels)}"}
    return {}


def run_all_validators(
    enrollment_id: Optional[int] = None,
    academic_period_id: Optional[int] = None,
    risk_score: Optional[Decimal] = None,
    risk_label: Optional[str] = None,
) -> Dict[str, str]:
    """Ejecuta todas las validaciones y retorna dict acumulado de errores."""
    errors = {}

    if enrollment_id is not None:
        errors.update(validate_enrollment_exists(enrollment_id))

    if academic_period_id is not None:
        errors.update(validate_academic_period_exists(academic_period_id))

    if risk_score is not None:
        errors.update(validate_risk_score_range(risk_score))

    if risk_label is not None:
        errors.update(validate_risk_label(risk_label))

    return errors
