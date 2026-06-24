from ..domain.entities import SubjectAcademicConfigEntity
from .models import SubjectAcademicConfig


def to_entity(model: SubjectAcademicConfig) -> SubjectAcademicConfigEntity:
    return SubjectAcademicConfigEntity(
        id=model.id,
        subject_id=model.subject_id,
        academic_grade_id=model.academic_grade_id,
        weekly_hours=model.weekly_hours,
        is_required=model.is_required,
        is_active=model.is_active,
    )
