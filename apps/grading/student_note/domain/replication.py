"""Replicación documental estilo CouchDB para notas de estudiante."""

from __future__ import annotations

import logging
import uuid as uuid_lib
from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.utils.dateparse import parse_datetime

from ..application import validators
from ..application.serializers import StudentNoteSerializer
from ..domain.services import StudentNoteService
from ..infrastructure.repositories import StudentNoteRepository

logger = logging.getLogger(__name__)


class StudentNoteReplicationService:
    repository = StudentNoteRepository

    @classmethod
    def _parse_score(cls, value):
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError):
            raise ValueError("numeric_score inválido")

    @classmethod
    def _writable_fields(cls, document: dict) -> dict:
        return {
            "enrollment_id": document.get("enrollment_id"),
            "evaluative_activity_id": document.get("evaluative_activity_id"),
            "numeric_score": cls._parse_score(document.get("numeric_score")),
            "qualitative_scale_id": document.get("qualitative_scale_id"),
            "teacher_observation": document.get("teacher_observation") or "",
            "grading_mode": document.get("grading_mode") or "NUMERIC",
            "device_origin": document.get("device_origin") or "mobile",
        }

    @classmethod
    def _find_by_natural_key(cls, document: dict):
        enrollment_id = document.get("enrollment_id")
        activity_id = document.get("evaluative_activity_id")
        if enrollment_id and activity_id:
            return cls.repository.get_by_composite_key(enrollment_id, activity_id)
        return None

    @classmethod
    @transaction.atomic
    def apply_document(cls, document: dict) -> dict:
        doc_uuid = str(document["uuid"])
        base_rev = int(document.get("base_rev", 0))
        fields = cls._writable_fields(document)

        try:
            errors = validators.run_all_validators(
                enrollment_id=fields["enrollment_id"],
                evaluative_activity_id=fields["evaluative_activity_id"],
                numeric_score=fields["numeric_score"],
            )
        except ValueError as exc:
            return {
                "uuid": doc_uuid,
                "status": "REJECTED",
                "rev": base_rev,
                "message": str(exc),
            }

        if errors:
            return {
                "uuid": doc_uuid,
                "status": "REJECTED",
                "rev": base_rev,
                "message": "; ".join(f"{k}: {v}" for k, v in errors.items()),
            }

        instance = cls.repository.model.objects.select_for_update().filter(
            uuid=doc_uuid
        ).first()

        if instance is None:
            instance = cls._find_by_natural_key(document)

        if instance is None:
            if base_rev != 0:
                return {
                    "uuid": doc_uuid,
                    "status": "CONFLICT",
                    "rev": 0,
                    "message": "El documento no existe en el servidor",
                }
            try:
                note = StudentNoteService.create_student_note(
                    enrollment_id=fields["enrollment_id"],
                    evaluative_activity_id=fields["evaluative_activity_id"],
                    numeric_score=fields["numeric_score"],
                    qualitative_scale_id=fields["qualitative_scale_id"],
                    teacher_observation=fields["teacher_observation"],
                    device_origin=fields["device_origin"],
                )
            except ValueError as exc:
                detail = exc.args[0] if exc.args else str(exc)
                if isinstance(detail, dict):
                    detail = "; ".join(f"{k}: {v}" for k, v in detail.items())
                return {
                    "uuid": doc_uuid,
                    "status": "REJECTED",
                    "rev": base_rev,
                    "message": str(detail),
                }
            note.uuid = uuid_lib.UUID(doc_uuid)
            note.sync_version = 1
            note.mark_synced()
            note.save(update_fields=["uuid", "sync_version", "sync_status", "synced_at", "updated_at"])
            return {
                "uuid": doc_uuid,
                "status": "APPLIED",
                "rev": note.sync_version,
                "document": StudentNoteSerializer(note).data,
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
                "document": StudentNoteSerializer(instance).data,
            }

        try:
            note = StudentNoteService.update_student_note(
                instance.id,
                numeric_score=fields["numeric_score"],
                qualitative_scale_id=fields["qualitative_scale_id"],
                teacher_observation=fields["teacher_observation"],
                grading_mode=fields["grading_mode"],
                device_origin=fields["device_origin"],
            )
        except ValueError as exc:
            detail = exc.args[0] if exc.args else str(exc)
            if isinstance(detail, dict):
                detail = "; ".join(f"{k}: {v}" for k, v in detail.items())
            return {
                "uuid": doc_uuid,
                "status": "REJECTED",
                "rev": instance.sync_version,
                "message": str(detail),
            }

        note.sync_version = instance.sync_version + 1
        note.mark_synced()
        note.save(update_fields=["sync_version", "sync_status", "synced_at", "updated_at"])

        return {
            "uuid": doc_uuid,
            "status": "APPLIED",
            "rev": note.sync_version,
            "document": StudentNoteSerializer(note).data,
        }

    @classmethod
    def apply_batch(cls, documents: list[dict]) -> list[dict]:
        return [cls.apply_document(doc) for doc in documents]

    @classmethod
    def get_changes(cls, *, since, evaluative_activity_id) -> list[dict]:
        parsed_since = parse_datetime(since) if since else None
        if since and parsed_since is None:
            logger.warning("student_note replicate/changes: since inválido %r", since)
            parsed_since = None

        qs = cls.repository.model.objects.filter(
            evaluative_activity_id=evaluative_activity_id,
        ).select_related(
            "enrollment__student__user__person",
            "evaluative_activity",
        )
        if parsed_since:
            qs = qs.filter(updated_at__gte=parsed_since)

        return [
            StudentNoteSerializer(row).data
            for row in qs.order_by("updated_at")
        ]
