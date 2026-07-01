from ..domain.entities import AcademicLevelEntity
from .models import AcademicLevel


def to_entity(model: AcademicLevel) -> AcademicLevelEntity:
    return AcademicLevelEntity(
        id=model.id,
        name=model.name,
        code=model.code,
        description=model.description or "",
        is_active=model.is_active,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
