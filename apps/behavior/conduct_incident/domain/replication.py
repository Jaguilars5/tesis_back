"""Replicación documental estilo CouchDB para incidentes de conducta."""

from __future__ import annotations

import logging
import uuid as uuid_lib

from django.db import transaction
from django.utils.dateparse import parse_date, parse_datetime

from ..application import validators
from ..application.serializers import ConductIncidentSerializer
from ..infrastructure.repositories import ConductIncidentRepository
from .services import ConductIncidentService

logger = logging.getLogger(__name__)


class ConductIncidentReplicationService:
    repository = ConductIncidentRepository

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
        return {
            "enrollment_id": document.get("enrollment_id"),
            "incident_type_id": document.get("incident_type_id"),
            "severity_id": document.get("severity_id"),
            "academic_period_id": document.get("academic_period_id"),
            "incident_date": cls._parse_date(document.get("incident_date")),
            "description": document.get("description") or "",
            "actions_taken": document.get("actions_taken") or "",
            "family_notified": bool(document.get("family_notified", False)),
            "device_origin": document.get("device_origin") or "mobile",
        }

    @classmethod
    @transaction.atomic
    def apply_document(cls, document: dict) -> dict:
        doc_uuid = str(document["uuid"])
        base_rev = int(document.get("base_rev", 0))
        fields = cls._writable_fields(document)

        errors = validators.run_all_validators(**fields)
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
            if base_rev != 0:
                return {
                    "uuid": doc_uuid,
                    "status": "CONFLICT",
                    "rev": 0,
                    "message": "El documento no existe en el servidor",
                }
            instance = cls.repository.model.objects.create(
                uuid=uuid_lib.UUID(doc_uuid),
                **{k: v for k, v in fields.items() if k != "device_origin"},
            )
            if fields["device_origin"]:
                instance.device_origin = fields["device_origin"]
            instance.sync_version = 1
            instance.mark_synced()
            instance.save()
            ConductIncidentService._enqueue_post_create(instance)
            return {
                "uuid": doc_uuid,
                "status": "APPLIED",
                "rev": instance.sync_version,
                "document": ConductIncidentSerializer(instance).data,
            }

        if base_rev != instance.sync_version:
            return {
                "uuid": doc_uuid,
                "status": "CONFLICT",
                "rev": instance.sync_version,
                "document": ConductIncidentSerializer(instance).data,
            }

        update_allowed = {
            "incident_type_id",
            "severity_id",
            "academic_period_id",
            "incident_date",
            "description",
            "actions_taken",
            "family_notified",
            "device_origin",
        }
        for key, value in fields.items():
            if key in update_allowed:
                setattr(instance, key, value)

        instance.sync_version = instance.sync_version + 1
        instance.mark_synced()
        instance.save()

        return {
            "uuid": doc_uuid,
            "status": "APPLIED",
            "rev": instance.sync_version,
            "document": ConductIncidentSerializer(instance).data,
        }

    @classmethod
    def apply_batch(cls, documents: list[dict]) -> list[dict]:
        return [cls.apply_document(doc) for doc in documents]

    @classmethod
    def get_changes(cls, *, since, academic_period_id=None) -> list[dict]:
        parsed_since = parse_datetime(since) if since else None
        if since and parsed_since is None:
            logger.warning("conduct replicate/changes: since inválido %r", since)
            parsed_since = None

        qs = cls.repository.model.objects.all().select_related(
            "enrollment__student__user__person",
            "incident_type",
            "severity",
            "academic_period",
        )
        if academic_period_id:
            qs = qs.filter(academic_period_id=academic_period_id)
        if parsed_since:
            qs = qs.filter(updated_at__gte=parsed_since)

        return [
            ConductIncidentSerializer(row).data
            for row in qs.order_by("updated_at")
        ]
