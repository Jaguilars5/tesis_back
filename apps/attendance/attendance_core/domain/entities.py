from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True, slots=True)
class AttendanceEntity:
    """Entidad de dominio para un registro de asistencia."""

    id: int | None
    enrollment_id: int
    teacher_subject_section_id: int
    academic_period_id: int
    attendance_date: date
    attendance_status_id: int
    absence_type_id: int | None
    observation: str
    class_schedule_id: int | None
    uuid: str | None
    sync_status: str
    sync_version: int
    device_origin: str | None
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
