"""
Mappers para convertir entre modelos Django y entities de dominio.
"""

from dataclasses import asdict
from typing import Optional

from ..domain.entities import EarlyAlertEntity
from .models import EarlyAlert


def to_entity(model: EarlyAlert) -> Optional[EarlyAlertEntity]:
    """Convierte un modelo EarlyAlert a entity de dominio."""
    if model is None:
        return None
    return EarlyAlertEntity(
        id=model.id,
        enrollment_id=model.enrollment_id,
        academic_period_id=model.academic_period_id,
        alert_type=model.alert_type,
        description=model.description,
        urgency_level=model.urgency_level,
        attended=model.attended,
        attended_by_user_id=model.attended_by_user_id,
        detected_at=model.detected_at,
        attended_at=model.attended_at,
        response_actions=model.response_actions,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def to_model_dict(entity: EarlyAlertEntity) -> dict:
    """Convierte una entity a dict para crear/actualizar modelo."""
    return asdict(entity)
