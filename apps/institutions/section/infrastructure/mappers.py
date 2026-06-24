from ..domain.entities import SectionEntity
from .models import Section


def to_entity(model: Section) -> SectionEntity:
    return SectionEntity(
        id=model.id,
        school_year_id=model.school_year_id,
        academic_grade_id=model.academic_grade_id,
        code=model.code,
        parallel=model.parallel,
        capacity=model.capacity,
        is_active=model.is_active,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
