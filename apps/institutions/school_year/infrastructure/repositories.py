from datetime import date

from apps.core.repositories.base import BaseRepository

from ..domain.repositories import SchoolYearRepositoryInterface
from .models import SchoolYear


class SchoolYearRepository(BaseRepository, SchoolYearRepositoryInterface):
    model = SchoolYear

    @classmethod
    def get_all(cls, active_only=True, search=None):
        queryset = super().get_all(active_only=active_only)
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
