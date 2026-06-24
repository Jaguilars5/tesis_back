from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class AcademicPeriodEntity:
    """Entidad de dominio para un período académico."""

    id: int | None
    name: str
    school_year_id: int
    period_type_id: int
    code: str
    start_date: date
    end_date: date
    year_weight: Decimal | None
    is_regular_period: bool
    is_active: bool
