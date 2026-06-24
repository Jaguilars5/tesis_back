from ..domain.entities import QualitativeScaleEntity
from .models import QualitativeScale


def to_entity(model: QualitativeScale) -> QualitativeScaleEntity:
    return QualitativeScaleEntity(
        id=model.id,
        code=model.code,
        name=model.name,
        description=model.description,
        numeric_equivalence=model.numeric_equivalence,
        is_active=model.is_active,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
