from apps.core.repositories.base import BaseRepository
from apps.institutions.models import Section


class SectionRepository(BaseRepository):
    model = Section

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.order_by("academic_grade__sequence_order", "parallel")

    @classmethod
    def get_by_school_year(cls, school_year_id):
        return cls.model.objects.filter(
            school_year_id=school_year_id
        ).select_related("academic_grade__academic_level").order_by(
            "academic_grade__sequence_order", "parallel"
        )

    @classmethod
    def get_by_grade(cls, academic_grade_id):
        return cls.model.objects.filter(
            academic_grade_id=academic_grade_id
        ).select_related("school_year", "academic_grade")
