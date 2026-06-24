from apps.core.repositories.base import BaseRepository

from ..domain.repositories import AcademicGradeRepositoryInterface
from .models import AcademicGrade


class AcademicGradeRepository(BaseRepository, AcademicGradeRepositoryInterface):
    model = AcademicGrade

    @classmethod
    def get_all(cls, active_only=True, search=None):
        queryset = super().get_all(active_only=active_only)
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset.order_by("name")

    @classmethod
    def get_by_sublevel(cls, sublevel_id):
        return cls.model.objects.filter(
            academic_sublevel_id=sublevel_id
        ).order_by("name")
