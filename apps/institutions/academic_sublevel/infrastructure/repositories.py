from apps.core.repositories.base import BaseRepository

from ..domain.repositories import AcademicSublevelRepositoryInterface
from .models import AcademicSublevel


class AcademicSublevelRepository(BaseRepository, AcademicSublevelRepositoryInterface):
    model = AcademicSublevel

    @classmethod
    def get_all(cls, active_only=True, search=None):
        queryset = super().get_all(active_only=active_only)
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset.select_related("academic_level").order_by("name")
