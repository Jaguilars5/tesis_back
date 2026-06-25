from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True, slots=True)
class SchoolYearEntity:
    """Entidad de dominio para un año escolar."""

    id: int | None
    start_date: date
    end_date: date
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
