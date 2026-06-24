import logging

from .domain.services import AttendanceService
from .infrastructure.models import Attendance
from apps.integration.tasks.sync_tasks import BaseSyncHandler, register_sync_handler

logger = logging.getLogger(__name__)


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
