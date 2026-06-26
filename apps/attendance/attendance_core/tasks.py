import logging

from celery import shared_task

from .domain.services import AttendanceService
from .infrastructure.models import Attendance
from apps.integration.tasks.sync_tasks import BaseSyncHandler, register_sync_handler

logger = logging.getLogger(__name__)


def _emit_socketio_event(user_id, event, data):
    """Publica un evento de Socket.IO a la sala ``user_{id}`` vía Redis.

    Mismo protocolo nativo de python-socketio usado por analytics para
    comunicarse con el servidor ASGI desde un worker de Celery.
    """
    try:
        import json
        import uuid

        import redis as redis_lib
        from django.conf import settings

        r = redis_lib.Redis.from_url(settings.SOCKETIO_REDIS_URL)
        message = json.dumps({
            "method": "emit",
            "event": event,
            "data": [data],
            "binary": False,
            "namespace": "/",
            "room": f"user_{user_id}",
            "skip_sid": None,
            "callback": None,
            "host_id": str(uuid.uuid4()),
        })
        r.publish("socketio", message)
        r.close()
        logger.info("[SOCKET.IO] Evento %s publicado a Redis para user_%s", event, user_id)
    except Exception:
        logger.warning("[SOCKET.IO] No se pudo publicar evento a Redis", exc_info=True)


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
        _emit_socketio_event(
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


@register_sync_handler("attendance")
class AttendanceSyncHandler(BaseSyncHandler):
    model = Attendance

    @classmethod
    def _apply(cls, record_uuid, payload):
        payload = payload or {}
        instance = AttendanceService.create_attendance(
            enrollment_id=_pick(payload, "enrollment_id", "enrollment"),
            teacher_subject_section_id=_pick(
                payload, "teacher_subject_section_id", "teacher_subject_section"
            ),
            academic_period_id=_pick(payload, "academic_period_id", "academic_period"),
            attendance_date=_pick(payload, "attendance_date"),
            attendance_status_id=_pick(
                payload, "attendance_status_id", "attendance_status"
            ),
            absence_type_id=_pick(payload, "absence_type_id", "absence_type"),
            observation=payload.get("observation") or "",
            device_origin=payload.get("device_origin") or "mobile",
        )

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
