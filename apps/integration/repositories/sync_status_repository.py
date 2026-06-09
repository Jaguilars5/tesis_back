from apps.core.repositories.base import BaseRepository
from ..models import SyncStatus


class SyncStatusRepository(BaseRepository):
    model = SyncStatus

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.order_by("name")

    @classmethod
    def get_by_code(cls, code):
        try:
            return cls.model.objects.get(code=code)
        except cls.model.DoesNotExist:
            return None
