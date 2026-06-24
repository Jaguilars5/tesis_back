"""
Validaciones de negocio para alertas tempranas.

Funciones puras que retornan dict {field: message} si fallan.
El service las orquesta y acumula errores.
"""

from typing import Dict, Optional

from apps.students.repositories.enrollment_repository import EnrollmentRepository
from apps.academic.academic_period.infrastructure.repositories import (
    AcademicPeriodRepository,
)

from ..infrastructure.models import EarlyAlert
from ..infrastructure.repositories import EarlyAlertRepository


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


def validate_not_duplicate(
    enrollment_id: int, academic_period_id: int, alert_type: str, exclude_id: Optional[int] = None
) -> Dict[str, str]:
    """Valida que no exista una alerta duplicada del mismo tipo para la misma matrícula/período."""
    qs = EarlyAlert.objects.filter(
        enrollment_id=enrollment_id,
        academic_period_id=academic_period_id,
        alert_type=alert_type,
        attended=False,
    )
    if exclude_id:
        qs = qs.exclude(id=exclude_id)
    if qs.exists():
        return {"alert_type": f"Ya existe una alerta activa de tipo '{alert_type}' para este estudiante en este período"}
    return {}


def validate_urgency_level(urgency_level: Optional[str]) -> Dict[str, str]:
    """Valida que el nivel de urgencia sea válido."""
    if urgency_level and urgency_level not in dict(EarlyAlert._meta.get_field("urgency_level").choices):
        return {"urgency_level": f"Nivel de urgencia '{urgency_level}' no válido"}
    return {}


def validate_alert_type(alert_type: Optional[str]) -> Dict[str, str]:
    """Valida que el tipo de alerta sea válido."""
    if alert_type and alert_type not in dict(EarlyAlert._meta.get_field("alert_type").choices):
        return {"alert_type": f"Tipo de alerta '{alert_type}' no válido"}
    return {}


def run_all_validators(
    enrollment_id: int,
    academic_period_id: int,
    alert_type: Optional[str] = None,
    urgency_level: Optional[str] = None,
    exclude_id: Optional[int] = None,
) -> Dict[str, str]:
    """
    Ejecuta todas las validaciones y retorna dict acumulado de errores.

    Si no hay errores, retorna dict vacío.
    """
    errors = {}

    errors.update(validate_enrollment_exists(enrollment_id))
    errors.update(validate_academic_period_exists(academic_period_id))

    if not errors:  # Solo validar duplicados si las FKs son válidas
        errors.update(validate_not_duplicate(enrollment_id, academic_period_id, alert_type or "", exclude_id))

    errors.update(validate_urgency_level(urgency_level))
    errors.update(validate_alert_type(alert_type))

    return errors
