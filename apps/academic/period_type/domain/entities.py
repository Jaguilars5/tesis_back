from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PeriodTypeEntity:
    id: int | None
    code: str
    name: str
    description: str
    divisions_per_year: int
    is_active: bool
