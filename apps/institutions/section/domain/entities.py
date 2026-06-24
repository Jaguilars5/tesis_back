from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class SectionEntity:
    id: int | None
    school_year_id: int
    academic_grade_id: int | None
    code: str
    parallel: str
    capacity: int
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
