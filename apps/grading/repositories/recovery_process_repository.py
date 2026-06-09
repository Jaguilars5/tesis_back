from apps.core.repositories.base import BaseRepository
from apps.grading.models import RecoveryProcess


class RecoveryProcessRepository(BaseRepository):
    model = RecoveryProcess

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.order_by("-start_date")

    @classmethod
    def get_active_by_enrollment(cls, enrollment_id):
        return cls.model.objects.filter(
            period_grade_summary__enrollment_id=enrollment_id,
            end_date__isnull=True,
        )

    @classmethod
    def get_by_period_grade_summary(cls, period_grade_summary_id):
        return cls.model.objects.filter(
            period_grade_summary_id=period_grade_summary_id,
        ).order_by("-start_date")
