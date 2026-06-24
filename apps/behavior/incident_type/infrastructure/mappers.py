from ..domain.entities import IncidentTypeEntity
from .models import IncidentType


def to_entity(model: IncidentType) -> IncidentTypeEntity:
    return IncidentTypeEntity(
        id=model.id,
        code=model.code,
        name=model.name,
        description=model.description,
        is_active=model.is_active,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
