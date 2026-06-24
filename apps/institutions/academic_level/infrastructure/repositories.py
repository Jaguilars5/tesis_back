from apps.core.repositories.base import BaseRepository

from ..domain.repositories import AcademicLevelRepositoryInterface
from .models import AcademicLevel


class AcademicLevelRepository(BaseRepository, AcademicLevelRepositoryInterface):
    model = AcademicLevel

    @classmethod
    def get_all(cls, active_only=True, search=None):
        queryset = super().get_all(active_only=active_only)
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset.order_by("name")
