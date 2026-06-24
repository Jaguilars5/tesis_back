from ..domain.entities import AbsenceTypeEntity
from .models import AbsenceType


def to_entity(model: AbsenceType) -> AbsenceTypeEntity:
    return AbsenceTypeEntity(
        id=model.id,
        code=model.code,
        name=model.name,
        description=model.description,
        is_active=model.is_active,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
