from apps.core.repositories.base import BaseRepository
from apps.attendance.models.skill_evaluation import SkillEvaluation


class SkillEvaluationRepository(BaseRepository):
    model = SkillEvaluation

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.order_by("-id")
