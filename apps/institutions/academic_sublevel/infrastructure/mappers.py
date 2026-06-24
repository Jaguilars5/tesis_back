from ..domain.entities import AcademicSublevelEntity
from .models import AcademicSublevel


def to_entity(model: AcademicSublevel) -> AcademicSublevelEntity:
    return AcademicSublevelEntity(
        id=model.id,
        academic_level_id=model.academic_level_id,
        code=model.code,
        name=model.name,
        description=model.description,
        is_active=model.is_active,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
