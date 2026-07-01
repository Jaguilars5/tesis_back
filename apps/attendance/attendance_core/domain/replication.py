"""Replicación documental estilo CouchDB para asistencia.

Cada documento tiene ``uuid`` (id estable) y ``sync_version`` (revisión).
El cliente envía ``base_rev``: la revisión en la que basó su edición.
Solo se aplica si ``base_rev == sync_version`` del servidor; si no, CONFLICT.
"""

from __future__ import annotations

import logging
import uuid as uuid_lib

from django.db import transaction
from django.utils.dateparse import parse_date, parse_datetime

from ..application import validators
from ..application.serializers import AttendanceSerializer
from ..infrastructure.repositories import AttendanceRepository
from .services import AttendanceService

logger = logging.getLogger(__name__)


class AttendanceReplicationService:
    repository = AttendanceRepository

    @classmethod
    def _parse_date(cls, value):
        if value is None:
            return None
        if hasattr(value, "year"):
            return value
        parsed = parse_date(str(value))
        if parsed is None:
            raise ValueError("Formato de fecha inválido. Use YYYY-MM-DD")
        return parsed

    @classmethod
    def _writable_fields(cls, document: dict) -> dict:
        attendance_date = cls._parse_date(document.get("attendance_date"))
        return {
            "enrollment_id": document.get("enrollment_id"),
            "teacher_subject_section_id": document.get("teacher_subject_section_id"),
            "academic_period_id": document.get("academic_period_id"),
            "attendance_date": attendance_date,
            "attendance_status_id": document.get("attendance_status_id"),
            "absence_type_id": document.get("absence_type_id"),
            "observation": document.get("observation") or "",
            "device_origin": document.get("device_origin") or "mobile",
            "class_schedule_id": document.get("class_schedule_id"),
        }

    @classmethod
    def _find_by_natural_key(cls, document: dict):
        fields = cls._writable_fields(document)
        enrollment_id = fields["enrollment_id"]
        attendance_date = fields["attendance_date"]
        schedule_id = fields["class_schedule_id"]
        tss_id = fields["teacher_subject_section_id"]

        if schedule_id and enrollment_id and attendance_date:
            return cls.repository.model.objects.select_for_update().filter(
                enrollment_id=enrollment_id,
                class_schedule_id=schedule_id,
                attendance_date=attendance_date,
            ).first()

        if tss_id and enrollment_id and attendance_date:
            return cls.repository.model.objects.select_for_update().filter(
                enrollment_id=enrollment_id,
                teacher_subject_section_id=tss_id,
                attendance_date=attendance_date,
            ).first()

        return None

    @classmethod
    def _validate_document(cls, fields: dict, existing_attendance=None) -> dict | None:
        is_status_change = validators.is_attendance_status_changing(
            existing_attendance,
            fields["attendance_status_id"],
            fields["absence_type_id"],
        )
        return validators.run_all_validators(
            enrollment_id=fields["enrollment_id"],
            teacher_subject_section_id=fields["teacher_subject_section_id"],
            academic_period_id=fields["academic_period_id"],
            attendance_date=fields["attendance_date"],
            attendance_status_id=fields["attendance_status_id"],
            absence_type_id=fields["absence_type_id"],
            observation=fields["observation"],
            device_origin=fields["device_origin"],
            class_schedule_id=fields["class_schedule_id"],
            existing_attendance=existing_attendance,
            is_status_change=is_status_change,
        )

    @classmethod
    @transaction.atomic
    def apply_document(cls, document: dict) -> dict:
        doc_uuid = str(document["uuid"])
        base_rev = int(document.get("base_rev", 0))
        fields = cls._writable_fields(document)

        instance = cls.repository.model.objects.select_for_update().filter(
            uuid=doc_uuid
        ).first()

        if instance is None:
            instance = cls._find_by_natural_key(document)

        errors = cls._validate_document(fields, existing_attendance=instance)
        if errors:
            return {
                "uuid": doc_uuid,
                "status": "REJECTED",
                "rev": base_rev if instance is None else instance.sync_version,
                "message": "; ".join(f"{k}: {v}" for k, v in errors.items()),
            }

        if instance is None:
            if base_rev != 0:
                return {
                    "uuid": doc_uuid,
                    "status": "CONFLICT",
                    "rev": 0,
                    "message": "El documento no existe en el servidor",
                }
            instance = cls.repository.model.objects.create(
                uuid=uuid_lib.UUID(doc_uuid),
                **{k: v for k, v in fields.items() if v is not None},
            )
            instance.sync_version = 1
            instance.mark_synced()
            instance.save(update_fields=["sync_status", "synced_at", "sync_version"])
            if fields["class_schedule_id"]:
                AttendanceService._check_schedule_day_warning(
                    instance,
                    fields["class_schedule_id"],
                    fields["attendance_date"],
                )
            AttendanceService._maybe_notify_absence(instance)
            AttendanceService._enqueue_attendance_notification(instance)
            return {
                "uuid": doc_uuid,
                "status": "APPLIED",
                "rev": instance.sync_version,
                "document": AttendanceSerializer(instance).data,
            }

        if str(instance.uuid) != doc_uuid and not cls.repository.model.objects.filter(
            uuid=doc_uuid
        ).exists():
            instance.uuid = uuid_lib.UUID(doc_uuid)
            instance.save(update_fields=["uuid"])

        if base_rev != instance.sync_version:
            return {
                "uuid": doc_uuid,
                "status": "CONFLICT",
                "rev": instance.sync_version,
                "document": AttendanceSerializer(instance).data,
            }

        update_allowed = {
            "academic_period_id",
            "attendance_status_id",
            "absence_type_id",
            "observation",
            "device_origin",
            "class_schedule_id",
        }
        for key, value in fields.items():
            if key in update_allowed:
                setattr(instance, key, value)

        instance.sync_version = instance.sync_version + 1
        instance.mark_synced()
        instance.save()

        AttendanceService._maybe_notify_absence(instance)
        AttendanceService._enqueue_attendance_notification(instance)

        return {
            "uuid": doc_uuid,
            "status": "APPLIED",
            "rev": instance.sync_version,
            "document": AttendanceSerializer(instance).data,
        }

    @classmethod
    def apply_batch(cls, documents: list[dict]) -> list[dict]:
        return [cls.apply_document(doc) for doc in documents]

    @classmethod
    def get_changes(
        cls,
        *,
        since,
        teacher_subject_section_id,
        academic_period_id,
        class_schedule_id,
    ) -> list[dict]:
        parsed_since = parse_datetime(since) if since else None
        if since and parsed_since is None:
            logger.warning("replicate/changes: since inválido %r", since)
            parsed_since = None

        qs = cls.repository.model.objects.filter(
            teacher_subject_section_id=teacher_subject_section_id,
            academic_period_id=academic_period_id,
            class_schedule_id=class_schedule_id,
        ).select_related(
            "attendance_status",
            "absence_type",
            "enrollment__student__user__person",
        )

        if parsed_since:
            qs = qs.filter(updated_at__gte=parsed_since)

        return [AttendanceSerializer(row).data for row in qs.order_by("updated_at")]
