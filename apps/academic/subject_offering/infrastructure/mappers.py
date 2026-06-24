from ..domain.entities import SubjectOfferingEntity
from .models import SubjectOffering


def to_entity(model: SubjectOffering) -> SubjectOfferingEntity:
    return SubjectOfferingEntity(
        id=model.id,
        section_id=model.section_id,
        subject_academic_config_id=model.subject_academic_config_id,
        is_active=model.is_active,
    )
