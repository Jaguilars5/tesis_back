from apps.core.repositories.base import BaseRepository

from ..domain.repositories import SubjectRepositoryInterface
from .models import Subject


class SubjectRepository(BaseRepository, SubjectRepositoryInterface):
    model = Subject

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.order_by("name")
