from datetime import date
from typing import TypedDict


class CreateAttendancePayload(TypedDict, total=False):
    enrollment_id: int
    teacher_subject_section_id: int
    academic_period_id: int
    attendance_date: date
    attendance_status_id: int
    absence_type_id: int | None
    observation: str
    class_schedule_id: int | None
    device_origin: str | None


class TakeBySchedulePayload(TypedDict, total=False):
    class_schedule_id: int
    date: str
    academic_period: int
    teacher_subject_section: int
    records: list[dict]
