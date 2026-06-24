from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True, slots=True)
class ConductIncidentEntity:
    """Entidad de dominio para un incidente de conducta."""

    id: int | None
    incident_type_id: int
    severity_id: int
    academic_period_id: int
    enrollment_id: int
    incident_date: date
    description: str
    actions_taken: str
    family_notified: bool
    uuid: str | None
    sync_status: str
    sync_version: int
    device_origin: str | None
    created_at: datetime | None = None
    updated_at: datetime | None = None
