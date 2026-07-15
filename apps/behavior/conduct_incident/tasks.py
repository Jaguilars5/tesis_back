import logging

from celery import shared_task
from django.db import transaction

from .infrastructure.models import ConductIncident
from apps.behavior.incident_type import IncidentType
from apps.integration.tasks.sync_tasks import BaseSyncHandler, register_sync_handler

logger = logging.getLogger(__name__)


@shared_task(bind=True, ignore_result=True)
def recalculate_conduct_average_task(self, enrollment_id, academic_period_id):
    """Recalcula la evaluación de conducta del estudiante para el periodo.

    Se encola al crear un incidente para mantener el promedio de conducta vivo.
    """
    from apps.behavior.behavior_evaluation.domain.services import (
        BehaviorEvaluationService,
    )

    if not (enrollment_id and academic_period_id):
        logger.warning(
            "recalculate_conduct_average_task skipped: enrollment=%s period=%s",
            enrollment_id, academic_period_id,
        )
        return None

    return BehaviorEvaluationService.calculate_behavior_evaluation(
        enrollment_id=enrollment_id,
        academic_period_id=academic_period_id,
    )


@register_sync_handler("conduct_incident")
class ConductIncidentSyncHandler(BaseSyncHandler):
    source_table = "conduct_incident"
    model = ConductIncident
    business_key_fields = ["enrollment_id", "incident_type_id", "incident_date"]

    @classmethod
    def _resolve_incident_type(cls, payload):
        category = payload.pop("incident_type", None) if payload else None
        if isinstance(category, str):
            incident_type_obj, _ = IncidentType.objects.get_or_create(
                code=category,
                defaults={"name": category.capitalize(), "description": f"Tipo de incidente: {category}"},
            )
            return incident_type_obj
        return category

    @classmethod
    def handle_insert(cls, record_uuid, payload):
        payload = payload or {}
        incident_type = cls._resolve_incident_type(payload)
        with transaction.atomic():
            instance = cls.model(**payload)
            instance.uuid = record_uuid
            instance.sync_status = "SYNCED"
            instance.synced_at = None
            instance.sync_version = 1
            if incident_type:
                instance.incident_type = incident_type
            instance.full_clean()
            instance.save()
        return instance

    @classmethod
    def handle_update(cls, record_uuid, payload):
        payload = payload or {}
        incident_type = cls._resolve_incident_type(payload)
        incoming_version = payload.get("sync_version", 1)
        with transaction.atomic():
            instance = cls.model.objects.get(uuid=record_uuid)
            if incoming_version < instance.sync_version:
                from apps.integration.services.conflict_resolver import ConflictResolutionStrategy
                resolution = ConflictResolutionStrategy.resolve(cls.source_table, instance, payload)
                if resolution in ("MANUAL", "KEEP_LOCAL"):
                    if resolution == "MANUAL":
                        instance.mark_conflict()
                        instance.save()
                    return {"status": resolution, "local_version": instance.sync_version, "uuid": str(instance.uuid)}
            for key, value in payload.items():
                if hasattr(instance, key) and key not in ["uuid", "sync_version", "id"]:
                    setattr(instance, key, value)
            if incident_type:
                instance.incident_type = incident_type
            instance.sync_version = max(instance.sync_version, incoming_version) + 1
            instance.mark_synced()
            instance.full_clean()
            instance.save()
        return instance
