from apps.core.repositories.base import BaseRepository
from apps.attendance.models.behavior_evaluation import BehaviorEvaluation


class BehaviorEvaluationRepository(BaseRepository):
    model = BehaviorEvaluation

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.order_by("-id")
