from apps.core.repositories.base import BaseRepository
from apps.behavior.models import IncidentType


class IncidentTypeRepository(BaseRepository):
    model = IncidentType

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.order_by("name")
