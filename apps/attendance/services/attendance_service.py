import logging
from datetime import date
from django.db import transaction
from ..repositories import AttendanceRepository, AttendanceStatusRepository

logger = logging.getLogger(__name__)


class AttendanceService:
    @staticmethod
    @transaction.atomic
    def create_attendance(enrollment_id, teacher_subject_section_id, academic_period_id,
                          attendance_date, attendance_status_id, absence_type_id=None,
                          observation="", device_origin=None, class_schedule_id=None):
        if class_schedule_id:
            existing = AttendanceRepository.get_by_unique_key_with_schedule(
                enrollment_id, class_schedule_id, attendance_date
            )
        else:
            existing = AttendanceRepository.get_by_unique_key(
                enrollment_id, teacher_subject_section_id, attendance_date
            )

        if existing:
            existing.academic_period_id = academic_period_id
            existing.attendance_status_id = attendance_status_id
            existing.absence_type_id = absence_type_id
            existing.observation = observation
            existing.device_origin = device_origin
            if class_schedule_id:
                existing.class_schedule_id = class_schedule_id
            existing.save()
            return existing

        from ..models import Attendance
        attendance = Attendance(
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
        attendance.save()

        if class_schedule_id:
            try:
                from apps.academic.models import ClassSchedule
                cs = ClassSchedule.objects.get(id=class_schedule_id)
                date_day = attendance_date.isoweekday()
                if cs.day_of_week != date_day:
                    logger.warning(
                        f"Attendance #{attendance.id}: date {attendance_date} (day {date_day}) "
                        f"doesn't match schedule day {cs.day_of_week} for ClassSchedule #{class_schedule_id}"
                    )
            except ClassSchedule.DoesNotExist:
                pass

        return attendance

    @staticmethod
    def get_attendance(attendance_id):
        attendance = AttendanceRepository.get_by_id(attendance_id)
        if not attendance:
            raise ValueError(f"Asistencia {attendance_id} no encontrada")
        return attendance

    @staticmethod
    def update_attendance(attendance_id, **kwargs):
        attendance = AttendanceService.get_attendance(attendance_id)
        for key, value in kwargs.items():
            if hasattr(attendance, key):
                setattr(attendance, key, value)
        attendance.save()
        return attendance

    @staticmethod
    def delete_attendance(attendance_id):
        attendance = AttendanceService.get_attendance(attendance_id)
        attendance.delete()
        return True
