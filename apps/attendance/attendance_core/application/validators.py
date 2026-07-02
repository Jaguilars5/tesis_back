"""
Validaciones de negocio para Attendance.
"""

from datetime import date, time


def _coerce_attendance_date(value):
    """Normaliza attendance_date a ``date`` cuando viene como string ISO del sync."""
    if value is None or isinstance(value, date):
        return value
    if isinstance(value, str):
        return date.fromisoformat(value)
    return value


def validate_required_fields(data, required):
    errors = {}
    for field in required:
        if field not in data or data[field] is None:
            errors[field] = f"{field} es obligatorio"
        elif isinstance(data[field], str) and not data[field].strip():
            errors[field] = f"{field} no puede estar vacío"
    return errors


def validate_attendance_date(value):
    if not value:
        return {}
    if isinstance(value, str):
        try:
            value = date.fromisoformat(value)
        except ValueError:
            return {"attendance_date": "Formato de fecha inválido. Use YYYY-MM-DD"}
    if value > date.today():
        return {"attendance_date": "La fecha de asistencia no puede ser futura"}
    return {}


def validate_academic_period_date(attendance_date, academic_period):
    from ..infrastructure.models import Attendance
    if attendance_date and academic_period:
        try:
            parsed_date = _coerce_attendance_date(attendance_date)
        except ValueError:
            return {"attendance_date": "Formato de fecha inválido. Use YYYY-MM-DD"}
        if parsed_date < academic_period.start_date or parsed_date > academic_period.end_date:
            return {
                "attendance_date": (
                    f"La fecha debe estar dentro del período académico "
                    f"({academic_period.start_date} - {academic_period.end_date})"
                )
            }
    return {}


def validate_enrollment_section(enrollment_id, teacher_subject_section_id):
    if enrollment_id and teacher_subject_section_id:
        from apps.students.models import Enrollment
        from apps.academic.teacher_subject_section.infrastructure.models import (
            TeacherSubjectSection,
        )
        try:
            enr = Enrollment.objects.get(id=enrollment_id)
            tss = TeacherSubjectSection.objects.get(id=teacher_subject_section_id)
            tss_section = tss.subject_offering.section_id
            if enr.section_id != tss_section:
                return {
                    "teacher_subject_section": "La clase no pertenece a la sección de la matrícula"
                }
        except (Enrollment.DoesNotExist, TeacherSubjectSection.DoesNotExist):
            return {"teacher_subject_section": "Matrícula o clase no encontrada"}
    return {}


def validate_class_schedule(schedule_id, teacher_subject_section_id, attendance_date):
    if schedule_id and teacher_subject_section_id:
        from apps.academic.class_schedule.infrastructure.models import ClassSchedule
        try:
            cs = ClassSchedule.objects.get(id=schedule_id)
            if cs.teacher_subject_section_id != teacher_subject_section_id:
                return {"class_schedule": "El horario no pertenece a la clase seleccionada"}
            if attendance_date:
                try:
                    parsed_date = _coerce_attendance_date(attendance_date)
                except ValueError:
                    return {"attendance_date": "Formato de fecha inválido. Use YYYY-MM-DD"}
                if cs.day_of_week != parsed_date.isoweekday():
                    return {
                        "class_schedule": (
                            f"La fecha ({parsed_date}, día {parsed_date.isoweekday()}) "
                            f"no coincide con el día del horario ({cs.day_of_week})"
                        )
                    }
        except ClassSchedule.DoesNotExist:
            return {"class_schedule": "Horario no encontrado"}
    return {}


def has_registered_attendance(attendance) -> bool:
    if attendance is None:
        return False
    return getattr(attendance, "attendance_status_id", None) is not None


def is_attendance_status_changing(
    existing,
    attendance_status_id,
    absence_type_id=None,
) -> bool:
    if existing is None:
        return attendance_status_id is not None
    if attendance_status_id is not None and existing.attendance_status_id != attendance_status_id:
        return True
    if absence_type_id is not None and existing.absence_type_id != absence_type_id:
        return True
    if (
        existing is not None
        and attendance_status_id is None
        and existing.attendance_status_id is not None
    ):
        return True
    return False


def validate_schedule_time_window(
    class_schedule_id,
    attendance_date,
    *,
    existing_attendance=None,
    is_status_change=False,
):
    """
    Restringe cambios de estado/ausencia fuera del bloque horario de la clase.

    - Hoy antes del inicio: no se puede registrar.
    - Hoy después del fin: no se puede modificar asistencia ya registrada.
    - Días anteriores: no se puede modificar asistencia ya registrada.
    """
    if not class_schedule_id or not attendance_date or not is_status_change:
        return {}

    from django.utils import timezone
    from apps.academic.class_schedule.infrastructure.models import ClassSchedule

    if isinstance(attendance_date, str):
        try:
            attendance_date = date.fromisoformat(attendance_date)
        except ValueError:
            return {"attendance_date": "Formato de fecha inválido. Use YYYY-MM-DD"}

    try:
        schedule = ClassSchedule.objects.get(pk=class_schedule_id)
    except ClassSchedule.DoesNotExist:
        return {"class_schedule": "Horario no encontrado"}

    today = timezone.localdate()
    now = timezone.localtime().time()
    start = schedule.start_time
    end = schedule.end_time
    time_label = f"{start.strftime('%H:%M')} - {end.strftime('%H:%M')}"

    if attendance_date > today:
        return {}

    if attendance_date < today:
        if has_registered_attendance(existing_attendance):
            return {
                "schedule_time": (
                    "No se puede modificar asistencia ya registrada de un día anterior."
                )
            }
        return {}

    # attendance_date == today
    if now < start:
        return {
            "schedule_time": (
                f"La asistencia solo puede registrarse durante el horario de clase "
                f"({time_label}). La clase aún no ha comenzado."
            )
        }

    if has_registered_attendance(existing_attendance) and now > end:
        return {
            "schedule_time": (
                f"El horario de clase ({time_label}) ya finalizó. "
                "No puede modificar asistencias ya registradas."
            )
        }

    return {}


def run_all_validators(**kwargs):
    errors = {}
    raw_date = kwargs.get("attendance_date")
    if isinstance(raw_date, str):
        try:
            kwargs["attendance_date"] = _coerce_attendance_date(raw_date)
        except ValueError:
            errors["attendance_date"] = "Formato de fecha inválido. Use YYYY-MM-DD"
            return errors

    errors.update(validate_required_fields(kwargs, [
        "enrollment_id", "teacher_subject_section_id",
        "academic_period_id", "attendance_date", "attendance_status_id",
    ]))
    errors.update(validate_attendance_date(kwargs.get("attendance_date")))
    errors.update(validate_enrollment_section(
        kwargs.get("enrollment_id"), kwargs.get("teacher_subject_section_id")
    ))
    errors.update(validate_class_schedule(
        kwargs.get("class_schedule_id"),
        kwargs.get("teacher_subject_section_id"),
        kwargs.get("attendance_date"),
    ))
    academic_period = kwargs.get("academic_period")
    if academic_period is None and kwargs.get("academic_period_id"):
        from apps.academic.academic_period.infrastructure.repositories import (
            AcademicPeriodRepository,
        )
        academic_period = AcademicPeriodRepository.get_by_id(
            kwargs.get("academic_period_id")
        )
    errors.update(validate_academic_period_date(
        kwargs.get("attendance_date"), academic_period
    ))
    errors.update(validate_schedule_time_window(
        kwargs.get("class_schedule_id"),
        kwargs.get("attendance_date"),
        existing_attendance=kwargs.get("existing_attendance"),
        is_status_change=kwargs.get("is_status_change", False),
    ))
    return errors
