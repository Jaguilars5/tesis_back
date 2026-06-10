from django.db import transaction
from apps.behavior.models import (
    ConductIncident, BehaviorEvaluation,
    SkillEvaluation, DiagnosticEvaluation,
)
from apps.integration.tasks.sync_tasks import BaseSyncHandler, register_sync_handler


@register_sync_handler("conduct_incident")
class ConductIncidentSyncHandler(BaseSyncHandler):
    source_table = "conduct_incident"
    model = ConductIncident

    @classmethod
    def handle_insert(cls, record_uuid, payload):
        category = payload.pop("category", None) if payload else None
        payload = payload or {}
        with transaction.atomic():
            instance = cls.model(**payload)
            instance.uuid = record_uuid
            instance.sync_status = "SYNCED"
            instance.synced_at = None
            instance.sync_version = 1
            if category:
                instance.category = category
            instance.full_clean()
            instance.save()
        return instance

    @classmethod
    def handle_update(cls, record_uuid, payload):
        category = payload.pop("category", None) if payload else None
        payload = payload or {}
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
            if category:
                instance.category = category
            instance.sync_version = max(instance.sync_version, incoming_version) + 1
            instance.mark_synced()
            instance.full_clean()
            instance.save()
        return instance


@register_sync_handler("behavior_evaluation")
class BehaviorEvaluationSyncHandler(BaseSyncHandler):
    source_table = "behavior_evaluation"
    model = BehaviorEvaluation


@register_sync_handler("skill_evaluation")
class SkillEvaluationSyncHandler(BaseSyncHandler):
    source_table = "skill_evaluation"
    model = SkillEvaluation


@register_sync_handler("diagnostic_evaluation")
class DiagnosticEvaluationSyncHandler(BaseSyncHandler):
    source_table = "diagnostic_evaluation"
    model = DiagnosticEvaluation
