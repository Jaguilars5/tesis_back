from ..domain.entities import ActivityTypeEntity
from .models import ActivityType


def to_entity(model: ActivityType) -> ActivityTypeEntity:
    return ActivityTypeEntity(
        id=model.id,
        code=model.code,
        name=model.name,
        description=model.description,
        is_active=model.is_active,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
