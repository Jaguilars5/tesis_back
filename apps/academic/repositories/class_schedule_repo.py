from apps.core.repositories.base import BaseRepository
from apps.academic.models import ClassSchedule, DayOfWeek


class DayOfWeekRepository(BaseRepository):
    model = DayOfWeek

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.order_by("code")


class ClassScheduleRepository(BaseRepository):
    model = ClassSchedule

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.order_by("day_of_week", "start_time")

    @classmethod
    def get_by_subject_offering(cls, subject_offering_id):
        return cls.model.objects.filter(
            subject_offering_id=subject_offering_id
        ).select_related("day_of_week")
