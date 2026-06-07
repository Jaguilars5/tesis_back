from apps.core.repositories.base import BaseRepository
from apps.grading.models import PeriodGradeSummary


class PeriodGradeSummaryRepository(BaseRepository):
    model = PeriodGradeSummary

    @classmethod
    def get_by_enrollment(cls, enrollment_id):
        return cls.model.objects.filter(
            enrollment_id=enrollment_id,
        ).select_related("subject_offering", "academic_period", "qualitative_scale")

    @classmethod
    def get_needing_recovery(cls, academic_period_id):
        return cls.model.objects.filter(
            academic_period_id=academic_period_id,
            requires_recovery=True,
        ).select_related("enrollment__student", "subject_offering")
