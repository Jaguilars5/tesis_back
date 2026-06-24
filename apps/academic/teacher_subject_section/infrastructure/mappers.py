from ..domain.entities import TeacherSubjectSectionEntity
from .models import TeacherSubjectSection


def to_entity(model: TeacherSubjectSection) -> TeacherSubjectSectionEntity:
    return TeacherSubjectSectionEntity(
        id=model.id,
        user_id=model.user_id,
        subject_offering_id=model.subject_offering_id,
        is_active=model.is_active,
    )
