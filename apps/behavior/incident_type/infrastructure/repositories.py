from apps.core.repositories.base import BaseRepository

from ..domain.repositories import IncidentTypeRepositoryInterface
from .models import IncidentType


class IncidentTypeRepository(BaseRepository, IncidentTypeRepositoryInterface):
    model = IncidentType

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.order_by("name")

    @classmethod
    def get_cascade_counts(cls, instance_id: int) -> dict[str, int]:
        return {}

    @classmethod
    def deactivate_cascade(cls, instance_id: int) -> int:
        cls.model.objects.filter(pk=instance_id).update(is_active=False)
        return 1
