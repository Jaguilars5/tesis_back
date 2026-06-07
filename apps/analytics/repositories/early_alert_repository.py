from apps.core.repositories.base import BaseRepository
from apps.analytics.models import EarlyAlert


class EarlyAlertRepository(BaseRepository):
    model = EarlyAlert

    @classmethod
    def get_pending_alerts(cls, urgency_level=None):
        filters = {"attended": False}
        if urgency_level:
            filters["urgency_level"] = urgency_level
        return cls.model.objects.filter(**filters).select_related("enrollment", "academic_period")

    @classmethod
    def get_by_enrollment(cls, enrollment_id):
        return cls.model.objects.filter(enrollment_id=enrollment_id).order_by("-detected_at")

    @classmethod
    def count_active_by_enrollment(cls, enrollment_id):
        return cls.model.objects.filter(enrollment_id=enrollment_id, attended=False).count()
