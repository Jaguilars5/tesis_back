from ..domain.entities import AttendanceEntity
from .models import Attendance


def to_entity(model: Attendance) -> AttendanceEntity:
    return AttendanceEntity(
        id=model.id,
        enrollment_id=model.enrollment_id,
        teacher_subject_section_id=model.teacher_subject_section_id,
        academic_period_id=model.academic_period_id,
        attendance_date=model.attendance_date,
        attendance_status_id=model.attendance_status_id,
        absence_type_id=model.absence_type_id,
        observation=model.observation,
        class_schedule_id=model.class_schedule_id,
        uuid=str(model.uuid) if model.uuid else None,
        sync_status=model.sync_status,
        sync_version=model.sync_version,
        device_origin=model.device_origin,
        is_active=model.is_active,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
