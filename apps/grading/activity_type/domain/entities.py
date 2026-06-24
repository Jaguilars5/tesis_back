from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class ActivityTypeEntity:
    """Entidad de dominio para un tipo de actividad evaluativa."""

    id: int | None
    code: str
    name: str
    description: str
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
