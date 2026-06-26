import logging

from django.db import transaction

from ..application import validators
from ..infrastructure.repositories import AttendanceRepository

logger = logging.getLogger(__name__)


class AttendanceService:
    """Lógica de negocio para registros de asistencia."""

    repository = AttendanceRepository

    @classmethod
    @transaction.atomic
    def create_attendance(cls, enrollment_id, teacher_subject_section_id, academic_period_id,
                          attendance_date, attendance_status_id, absence_type_id=None,
                          observation="", device_origin=None, class_schedule_id=None):
        errors = validators.run_all_validators(
            enrollment_id=enrollment_id,
            teacher_subject_section_id=teacher_subject_section_id,
            academic_period_id=academic_period_id,
            attendance_date=attendance_date,
            attendance_status_id=attendance_status_id,
            absence_type_id=absence_type_id,
            observation=observation,
            device_origin=device_origin,
            class_schedule_id=class_schedule_id,
        )
        if errors:
            raise ValueError(errors)

        if class_schedule_id:
            existing = cls.repository.get_by_unique_key_with_schedule(
                enrollment_id, class_schedule_id, attendance_date
            )
        else:
            existing = cls.repository.get_by_unique_key(
                enrollment_id, teacher_subject_section_id, attendance_date
            )

        if existing:
            return cls.repository.update(
                existing.id,
                academic_period_id=academic_period_id,
                attendance_status_id=attendance_status_id,
                absence_type_id=absence_type_id,
                observation=observation,
                device_origin=device_origin,
                class_schedule_id=class_schedule_id,
            )

        attendance = cls.repository.create(
            enrollment_id=enrollment_id,
            teacher_subject_section_id=teacher_subject_section_id,
            academic_period_id=academic_period_id,
            attendance_date=attendance_date,
            attendance_status_id=attendance_status_id,
            absence_type_id=absence_type_id,
            observation=observation,
            device_origin=device_origin,
            class_schedule_id=class_schedule_id,
        )

        if class_schedule_id:
            cls._check_schedule_day_warning(attendance, class_schedule_id, attendance_date)

        return attendance

    @classmethod
    def _check_schedule_day_warning(cls, attendance, class_schedule_id, attendance_date):
        schedule_day = cls.repository.get_schedule_day(class_schedule_id)
        if schedule_day is not None:
            date_day = attendance_date.isoweekday()
            if schedule_day != date_day:
                logger.warning(
                    f"Attendance #{attendance.id}: date {attendance_date} (day {date_day}) "
                    f"doesn't match schedule day {schedule_day} for ClassSchedule #{class_schedule_id}"
                )

    @classmethod
    def get_attendance(cls, attendance_id):
        attendance = cls.repository.get_by_id(attendance_id)
        if not attendance:
            raise ValueError(f"Asistencia {attendance_id} no encontrada")
        return attendance

    @classmethod
    def update_attendance(cls, attendance_id, **kwargs):
        cls.get_attendance(attendance_id)
        allowed = {
            "academic_period_id", "attendance_status_id", "absence_type_id",
            "observation", "device_origin", "class_schedule_id",
        }
        clean = {k: v for k, v in kwargs.items() if k in allowed}
        return cls.repository.update(attendance_id, **clean)

    @classmethod
    def delete_attendance(cls, attendance_id):
        cls.get_attendance(attendance_id)
        cls.repository.delete(attendance_id)
        return True

    @classmethod
    def soft_delete(cls, pk, confirm=False):
        obj = cls.get_attendance(pk)
        counts = cls.repository.get_cascade_counts(pk)
        total = sum(counts.values())

        if total > 0 and not confirm:
            parts = [f"{v} {k}" for k, v in counts.items()]
            return {
                "requires_confirmation": True,
                "affected_records": total,
                "message": f"Esta acción desactivará {', '.join(parts)} relacionados",
                "id": obj.id,
                "is_active": True,
            }

        total = cls.repository.deactivate_cascade(pk)
        return {
            "id": obj.id,
            "is_active": False,
            "deactivated_records": total,
        }
