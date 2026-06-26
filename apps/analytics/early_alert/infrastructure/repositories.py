from typing import List, Optional

from apps.core.repositories.base import BaseRepository

from ..domain.repositories import EarlyAlertRepositoryInterface
from .models import EarlyAlert


class EarlyAlertRepository(BaseRepository, EarlyAlertRepositoryInterface):
    model = EarlyAlert

    @classmethod
    def get_all(cls, active_only: bool = True):
        qs = cls.model.objects.all()
        return qs.select_related("enrollment", "academic_period", "attended_by_user")

    @classmethod
    def get_by_id(cls, pk: int) -> Optional[EarlyAlert]:
        try:
            return cls.model.objects.select_related(
                "enrollment", "academic_period", "attended_by_user"
            ).get(pk=pk)
        except cls.model.DoesNotExist:
            return None

    @classmethod
    def get_pending_alerts(
        cls, urgency_level: Optional[str] = None
    ) -> List[EarlyAlert]:
        filters = {"attended": False}
        if urgency_level:
            filters["urgency_level"] = urgency_level
        return (
            cls.model.objects.filter(**filters)
            .select_related("enrollment", "academic_period")
            .order_by("-detected_at")
        )

    @classmethod
    def get_by_enrollment(cls, enrollment_id: int) -> List[EarlyAlert]:
        return (
            cls.model.objects.filter(enrollment_id=enrollment_id)
            .select_related("enrollment", "academic_period")
            .order_by("-detected_at")
        )

    @classmethod
    def count_active_by_enrollment(cls, enrollment_id: int) -> int:
        return cls.model.objects.filter(
            enrollment_id=enrollment_id, attended=False
        ).count()

    @classmethod
    def get_pending_count(cls) -> int:
        return cls.model.objects.filter(attended=False).count()

    @classmethod
    def get_by_urgency(cls, urgency_level: str) -> List[EarlyAlert]:
        return (
            cls.model.objects.filter(urgency_level=urgency_level)
            .select_related("enrollment", "academic_period")
            .order_by("-detected_at")
        )
