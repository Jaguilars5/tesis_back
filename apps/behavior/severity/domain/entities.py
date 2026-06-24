from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class SeverityEntity:
    """Entidad de dominio para una severidad."""

    id: int | None
    code: str
    name: str
    description: str
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
