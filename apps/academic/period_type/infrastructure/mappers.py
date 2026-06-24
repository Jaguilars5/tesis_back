from ..domain.entities import PeriodTypeEntity
from .models import PeriodType


def to_entity(model: PeriodType) -> PeriodTypeEntity:
    return PeriodTypeEntity(
        id=model.id,
        code=model.code,
        name=model.name,
        description=model.description,
        divisions_per_year=model.divisions_per_year,
        is_active=model.is_active,
    )
