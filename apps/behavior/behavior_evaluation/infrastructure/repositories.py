from apps.core.repositories.base import BaseRepository

from ..domain.repositories import BehaviorEvaluationRepositoryInterface
from .models import BehaviorEvaluation


class BehaviorEvaluationRepository(BaseRepository, BehaviorEvaluationRepositoryInterface):
    model = BehaviorEvaluation

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.order_by("-id")
