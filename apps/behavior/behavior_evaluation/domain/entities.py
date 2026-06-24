from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True, slots=True)
class BehaviorEvaluationEntity:
    """Entidad de dominio para una evaluación de conducta."""

    id: int | None
    enrollment_id: int
    academic_period_id: int
    evaluated_by_id: int | None
    approved_by_id: int | None
    created_by_id: int | None
    calculated_scale_id: int
    final_scale_id: int | None
    general_observation: str
    override_reason: str
    evaluation_date: date
    approval_date: date | None
    uuid: str | None
    sync_status: str
    sync_version: int
    device_origin: str | None
    created_at: datetime | None = None
    updated_at: datetime | None = None
