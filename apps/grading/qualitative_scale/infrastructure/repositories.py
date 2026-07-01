from apps.core.repositories.base import BaseRepository

from ..domain.repositories import QualitativeScaleRepositoryInterface
from .models import QualitativeScale


class QualitativeScaleRepository(BaseRepository, QualitativeScaleRepositoryInterface):
    model = QualitativeScale

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.order_by("name")

    @classmethod
    def get_by_code(cls, code):
        try:
            return cls.model.objects.get(code=code)
        except cls.model.DoesNotExist:
            return None

    @classmethod
    def get_cascade_counts(cls, instance_id: int) -> dict[str, int]:
        return {}

    @classmethod
    def deactivate_cascade(cls, instance_id: int) -> int:
        cls.model.objects.filter(pk=instance_id).update(is_active=False)
        return 1
