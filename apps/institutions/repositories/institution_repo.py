from datetime import date
from apps.core.repositories.base import BaseRepository
from ..models import AcademicGrade, AcademicLevel, AcademicSublevel, SchoolYear


class SchoolYearRepository(BaseRepository):
    model = SchoolYear

    @classmethod
    def get_all(cls, active_only=True, search=None):
        queryset = super().get_all(active_only=active_only)
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset.order_by("-start_date")

    @classmethod
    def get_current(cls):
        today = date.today()
        return cls.model.objects.filter(
            start_date__lte=today,
            end_date__gte=today,
            is_active=True,
        ).first()

    @classmethod
    def has_overlap(cls, start_date, end_date, exclude_id=None):
        queryset = cls.model.objects.filter(
            start_date__lte=end_date, end_date__gte=start_date
        )
        if exclude_id:
            queryset = queryset.exclude(pk=exclude_id)
        return queryset.exists()


class AcademicLevelRepository(BaseRepository):
    model = AcademicLevel

    @classmethod
    def get_all(cls, active_only=True, search=None):
        queryset = super().get_all(active_only=active_only)
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset.order_by("name")


class AcademicGradeRepository(BaseRepository):
    model = AcademicGrade

    @classmethod
    def get_all(cls, active_only=True, search=None):
        queryset = super().get_all(active_only=active_only)
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset.order_by("sequence_order")

    @classmethod
    def get_by_sublevel(cls, sublevel_id):
        return cls.model.objects.filter(academic_sublevel_id=sublevel_id).order_by(
            "sequence_order"
        )


class AcademicSublevelRepository(BaseRepository):
    model = AcademicSublevel

    @classmethod
    def get_all(cls, active_only=True, search=None):
        queryset = super().get_all(active_only=active_only)
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset.select_related("academic_level").order_by("name")
