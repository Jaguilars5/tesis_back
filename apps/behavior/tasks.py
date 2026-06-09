import logging

from django.db import transaction

from apps.behavior.models import ConductIncident
from apps.integration.tasks.sync_tasks import BaseSyncHandler, register_sync_handler

logger = logging.getLogger(__name__)


@register_sync_handler("conduct_incident")
class ConductIncidentSyncHandler(BaseSyncHandler):
    model = ConductIncident

    @classmethod
    def handle_insert(cls, record_uuid, payload):
        category = payload.pop("category", None) if payload else None
        with transaction.atomic():
            instance = cls.model(**payload)
            if category:
                instance.category = category
            instance.full_clean()
            instance.save()
        return instance

    @classmethod
    def handle_update(cls, record_uuid, payload):
        category = payload.pop("category", None) if payload else None
        with transaction.atomic():
            instance = cls.model.objects.get(uuid=record_uuid)
            for key, value in payload.items():
                setattr(instance, key, value)
            if category:
                instance.category = category
            instance.full_clean()
            instance.save()
        return instance
