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
            update_data = {
                "academic_period_id": academic_period_id,
                "attendance_status_id": attendance_status_id,
                "absence_type_id": absence_type_id,
                "observation": observation,
                "device_origin": device_origin,
            }
            # Solo tocar class_schedule si se envió explícitamente, para no
            # borrar el horario de registros ya asociados a un bloque.
            if class_schedule_id is not None:
                update_data["class_schedule_id"] = class_schedule_id
            attendance = cls.repository.update(existing.id, **update_data)
        else:
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

        cls._maybe_notify_absence(attendance)

        return attendance

    @classmethod
    def _maybe_notify_absence(cls, attendance):
        """Programa la notificación a representantes si la asistencia es una falta.

        Se usa ``transaction.on_commit`` para que el aviso solo se dispare
        cuando la transacción del registro se haya confirmado correctamente.
        """
        try:
            status = attendance.attendance_status
            if not status or status.code != "A":
                return
            from ..tasks import notify_representatives_of_absence

            transaction.on_commit(
                lambda: notify_representatives_of_absence.delay(attendance.id)
            )
        except Exception:
            logger.warning(
                "No se pudo programar la notificación de falta para attendance=%s",
                getattr(attendance, "id", None),
                exc_info=True,
            )

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
