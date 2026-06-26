from apps.core.repositories.base import BaseRepository
from apps.grading.qualitative_scale import QualitativeScaleRepository
from apps.grading.qualitative_scale.infrastructure.models import QualitativeScale

from ..domain.repositories import BehaviorEvaluationRepositoryInterface
from .models import BehaviorEvaluation


class BehaviorEvaluationRepository(BaseRepository, BehaviorEvaluationRepositoryInterface):
    model = BehaviorEvaluation

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.order_by("-id")

    @classmethod
    def get_qualitative_scale_by_code(cls, code):
        return QualitativeScaleRepository.get_by_code(code)

    @classmethod
    def get_or_create_qualitative_scale(cls, code, defaults=None):
        scale = cls.get_qualitative_scale_by_code(code)
        if scale:
            return scale
        scale, _ = QualitativeScale.objects.get_or_create(
            code=code,
            defaults=defaults or {},
        )
        return scale
