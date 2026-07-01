import logging

from celery import shared_task

from .domain.services import AttendanceService
from .infrastructure.models import Attendance
from apps.core.realtime.emitter import emit_to_user
from apps.integration.tasks.sync_tasks import BaseSyncHandler, register_sync_handler

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def notify_representatives_of_absence(self, attendance_id):
    """Notifica a los representantes activos cuando un estudiante falta a clase.

    Envía por dos canales: in-app en tiempo real (Socket.IO) y correo
    electrónico, respetando el flag ``receives_notifications`` del representante.
    """
    from django.conf import settings
    from django.core.mail import send_mail

    from apps.students.repositories.students_repo import (
        StudentRepresentativeRepository,
    )
    from .infrastructure.repositories import AttendanceRepository

    attendance = AttendanceRepository.get_by_id(attendance_id)
    if not attendance:
        logger.warning("Asistencia %s no encontrada; se omite notificación", attendance_id)
        return {"skipped": "attendance_not_found", "attendance_id": attendance_id}

    # Solo se notifica una ausencia injustificada.
    if not attendance.attendance_status or attendance.attendance_status.code != "A":
        return {"skipped": "not_an_absence", "attendance_id": attendance_id}

    student = attendance.enrollment.student
    student_name = student.get_full_name() or f"Estudiante #{student.id}"

    reps = StudentRepresentativeRepository.get_by_student(student.id).filter(
        receives_notifications=True,
        is_active=True,
    )

    subject_label = str(attendance.teacher_subject_section) if attendance.teacher_subject_section_id else "una de sus clases"
    body = (
        f"Estimado/a representante, le informamos que {student_name} registró una "
        f"falta el día {attendance.attendance_date} en {subject_label}."
    )

    notified = 0
    for rep in reps:
        emit_to_user(
            rep.user_id,
            "absence_notification",
            {
                "attendance_id": attendance.id,
                "student_id": student.id,
                "student": student_name,
                "date": str(attendance.attendance_date),
                "subject": subject_label,
                "message": body,
            },
        )

        person = getattr(rep.user, "person", None)
        email = getattr(person, "email", "") if person else ""
        if email:
            send_mail(
                subject=f"Notificación de inasistencia - {student_name}",
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True,
            )

        notified += 1

    logger.info(
        "Notificación de falta enviada attendance=%s student=%s representantes=%s",
        attendance.id,
        student.id,
        notified,
    )
    return {"attendance_id": attendance.id, "notified": notified}


def _pick(payload, *keys):
    for key in keys:
        value = payload.get(key)
        if value is not None:
            return value
    return None


def _writable_fields(payload):
    """Campos editables de una asistencia presentes en el payload.

    Solo incluye una clave si el cliente la envió, para no sobrescribir con
    ``None`` campos que el cliente no pretendía tocar (p. ej. ``class_schedule``).
    """
    fields = {}

    period = _pick(payload, "academic_period_id", "academic_period")
    if period is not None:
        fields["academic_period_id"] = period

    status = _pick(payload, "attendance_status_id", "attendance_status")
    if status is not None:
        fields["attendance_status_id"] = status

    if "absence_type_id" in payload or "absence_type" in payload:
        fields["absence_type_id"] = _pick(payload, "absence_type_id", "absence_type")

    if "observation" in payload:
        fields["observation"] = payload.get("observation") or ""

    schedule = _pick(payload, "class_schedule_id", "class_schedule")
    if schedule is not None:
        fields["class_schedule_id"] = schedule

    fields["device_origin"] = payload.get("device_origin") or "mobile"
    return fields


@register_sync_handler("attendance")
class AttendanceSyncHandler(BaseSyncHandler):
    model = Attendance

    @classmethod
    def _apply(cls, record_uuid, payload):
        payload = payload or {}

        existing = cls.model.objects.filter(uuid=record_uuid).first()

        if existing is None:
            enrollment_id = _pick(payload, "enrollment_id", "enrollment")
            attendance_date = _pick(payload, "attendance_date")
            schedule_id = _pick(payload, "class_schedule_id", "class_schedule")
            tss_id = _pick(
                payload, "teacher_subject_section_id", "teacher_subject_section"
            )

            if schedule_id and enrollment_id and attendance_date:
                existing = cls.model.objects.filter(
                    enrollment_id=enrollment_id,
                    class_schedule_id=schedule_id,
                    attendance_date=attendance_date,
                ).first()
            elif tss_id and enrollment_id and attendance_date:
                existing = cls.model.objects.filter(
                    enrollment_id=enrollment_id,
                    teacher_subject_section_id=tss_id,
                    attendance_date=attendance_date,
                ).first()

        if existing is not None:
            instance = AttendanceService.update_attendance(
                existing.id, **_writable_fields(payload)
            )
            if str(instance.uuid) != str(record_uuid) and not cls.model.objects.filter(
                uuid=record_uuid
            ).exists():
                instance.uuid = record_uuid
                instance.save(update_fields=["uuid"])
        else:
            instance = AttendanceService.create_attendance(
                enrollment_id=_pick(payload, "enrollment_id", "enrollment"),
                teacher_subject_section_id=_pick(
                    payload, "teacher_subject_section_id", "teacher_subject_section"
                ),
                academic_period_id=_pick(
                    payload, "academic_period_id", "academic_period"
                ),
                attendance_date=_pick(payload, "attendance_date"),
                attendance_status_id=_pick(
                    payload, "attendance_status_id", "attendance_status"
                ),
                absence_type_id=_pick(payload, "absence_type_id", "absence_type"),
                observation=payload.get("observation") or "",
                device_origin=payload.get("device_origin") or "mobile",
                class_schedule_id=_pick(payload, "class_schedule_id", "class_schedule"),
            )
            # El uuid lo genera el cliente offline; si create_attendance creó una
            # fila nueva, se alinea el uuid para que ambos lados compartan la
            # misma identidad y el próximo pull no genere un duplicado.
            if str(instance.uuid) != str(record_uuid) and not cls.model.objects.filter(
                uuid=record_uuid
            ).exists():
                instance.uuid = record_uuid
                instance.save(update_fields=["uuid"])

        incoming_version = payload.get("sync_version")
        if incoming_version:
            instance.sync_version = max(instance.sync_version, int(incoming_version))
        instance.mark_synced()
        instance.save(update_fields=["sync_status", "synced_at", "sync_version"])

        return {"status": "SYNCED", "uuid": str(instance.uuid)}

    @classmethod
    def handle_insert(cls, record_uuid, payload):
        return cls._apply(record_uuid, payload)

    @classmethod
    def handle_update(cls, record_uuid, payload):
        return cls._apply(record_uuid, payload)

    @classmethod
    def handle_delete(cls, record_uuid, payload=None):
        cls.model.objects.filter(uuid=record_uuid).delete()
        return {"status": "DELETED", "uuid": str(record_uuid)}
