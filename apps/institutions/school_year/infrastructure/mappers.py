from ..domain.entities import SchoolYearEntity
from .models import SchoolYear


def to_entity(model: SchoolYear) -> SchoolYearEntity:
    return SchoolYearEntity(
        id=model.id,
        start_date=model.start_date,
        end_date=model.end_date,
        is_active=model.is_active,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
