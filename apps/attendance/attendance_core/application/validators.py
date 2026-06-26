"""
Validaciones de negocio para Attendance.
"""

from datetime import date


def validate_required_fields(data, required):
    errors = {}
    for field in required:
        if field not in data or data[field] is None:
            errors[field] = f"{field} es obligatorio"
        elif isinstance(data[field], str) and not data[field].strip():
            errors[field] = f"{field} no puede estar vacío"
    return errors


def validate_attendance_date(value):
    if value and value > date.today():
        return {"attendance_date": "La fecha de asistencia no puede ser futura"}
    return {}


def validate_academic_period_date(attendance_date, academic_period):
    from ..infrastructure.models import Attendance
    if attendance_date and academic_period:
        if attendance_date < academic_period.start_date or attendance_date > academic_period.end_date:
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
        from apps.academic_teacher_subject.models import TeacherSubjectSection
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
            if attendance_date and cs.day_of_week != attendance_date.isoweekday():
                return {
                    "class_schedule": (
                        f"La fecha ({attendance_date}, día {attendance_date.isoweekday()}) "
                        f"no coincide con el día del horario ({cs.day_of_week})"
                    )
                }
        except ClassSchedule.DoesNotExist:
            return {"class_schedule": "Horario no encontrado"}
    return {}


def run_all_validators(**kwargs):
    errors = {}
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
    return errors
