from ..domain.entities import SubjectEntity
from .models import Subject


def to_entity(model: Subject) -> SubjectEntity:
    return SubjectEntity(
        id=model.id,
        name=model.name,
        code=model.code,
        is_active=model.is_active,
    )
