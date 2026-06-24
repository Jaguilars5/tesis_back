from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class AttendanceStatusEntity:
    """Entidad de dominio para un estado de asistencia."""

    id: int | None
    code: str
    name: str
    description: str
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
