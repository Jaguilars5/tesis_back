from ..domain.entities import AcademicGradeEntity
from .models import AcademicGrade


def to_entity(model: AcademicGrade) -> AcademicGradeEntity:
    return AcademicGradeEntity(
        id=model.id,
        academic_sublevel_id=model.academic_sublevel_id,
        code=model.code or "",
        name=model.name,
        is_active=model.is_active,
    )
