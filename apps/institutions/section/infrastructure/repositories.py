from apps.core.repositories.base import BaseRepository

from ..domain.repositories import SectionRepositoryInterface
from .models import Section


class SectionRepository(BaseRepository, SectionRepositoryInterface):
    model = Section

    @classmethod
    def get_all(cls, active_only=True, search=None):
        queryset = super().get_all(active_only=active_only)
        if search:
            queryset = queryset.filter(parallel__icontains=search)
        return queryset.order_by("academic_grade__name", "parallel")

    @classmethod
    def get_by_school_year(cls, school_year_id):
        return cls.model.objects.filter(
            school_year_id=school_year_id
        ).select_related("academic_grade__academic_level").order_by(
            "academic_grade__name", "parallel"
        )

    @classmethod
    def get_by_grade(cls, academic_grade_id):
        return cls.model.objects.filter(
            academic_grade_id=academic_grade_id
        ).select_related("school_year", "academic_grade")
