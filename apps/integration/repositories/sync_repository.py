from ..models import SyncQueue
from apps.core.repositories.base import BaseRepository


class SyncQueueRepository(BaseRepository):
    model = SyncQueue

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.select_related("status", "operation", "user").order_by("-created_at")

    @classmethod
    def get_pending(cls):
        return cls.model.objects.filter(
            status__code__in=["PENDIENTE"]
        ).select_related("status", "operation").order_by("created_at")

    @classmethod
    def get_failed(cls):
        return cls.model.objects.filter(
            status__code__in=["ERROR"]
        ).select_related("status", "operation").order_by("-created_at")
