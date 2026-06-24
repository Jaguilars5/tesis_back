from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class AcademicLevelEntity:
    id: int | None
    name: str
    code: str
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
