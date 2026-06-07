from apps.core.repositories.base import BaseRepository
from apps.core.models import SyncQueue


class SyncQueueRepository(BaseRepository):
    model = SyncQueue

    @classmethod
    def get_pending(cls):
        return cls.model.objects.filter(status__in=["PENDIENTE", "pending"]).order_by("created_at")

    @classmethod
    def get_failed(cls):
        return cls.model.objects.filter(status__in=["ERROR", "failed"]).order_by("-created_at")
