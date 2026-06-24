from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class QualitativeScaleEntity:
    """Entidad de dominio para una escala cualitativa."""

    id: int | None
    code: str
    name: str
    description: str
    numeric_equivalence: Decimal
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
