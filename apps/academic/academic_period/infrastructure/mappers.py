from ..domain.entities import AcademicPeriodEntity
from .models import AcademicPeriod


def to_entity(model: AcademicPeriod) -> AcademicPeriodEntity:
    return AcademicPeriodEntity(
        id=model.id,
        name=model.name,
        school_year_id=model.school_year_id,
        period_type_id=model.period_type_id,
        code=model.code,
        start_date=model.start_date,
        end_date=model.end_date,
        year_weight=model.year_weight,
        is_regular_period=model.is_regular_period,
        is_active=model.is_active,
    )
