from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class AcademicSublevelEntity:
    id: int | None
    academic_level_id: int
    code: str
    name: str
    description: str
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
