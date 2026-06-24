from apps.core.repositories.base import BaseRepository

from ..domain.repositories import ActivityTypeRepositoryInterface
from .models import ActivityType


class ActivityTypeRepository(BaseRepository, ActivityTypeRepositoryInterface):
    model = ActivityType

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.order_by("name")
