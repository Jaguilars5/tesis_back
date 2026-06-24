from datetime import date
from decimal import Decimal
from typing import TypedDict


class ValidationErrors(TypedDict, total=False):
    school_year: str
    period_type: str
    start_date: str
    year_weight: str
    non_field_errors: str


class CreateAcademicPeriodPayload(TypedDict, total=False):
    name: str
    school_year_id: int
    period_type: str | object
    start_date: date
    end_date: date
    is_regular_period: bool
    year_weight: Decimal | None
