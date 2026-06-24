from ..domain.entities import SeverityEntity
from .models import Severity


def to_entity(model: Severity) -> SeverityEntity:
    return SeverityEntity(
        id=model.id,
        code=model.code,
        name=model.name,
        description=model.description,
        is_active=model.is_active,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
