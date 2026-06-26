from apps.core.repositories.base import BaseRepository

from ..domain.repositories import (
    QualitativeScaleRepositoryInterface,
    QualitativeScaleSublevelRepositoryInterface,
)
from .models import QualitativeScale, QualitativeScaleSublevel


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
        child_ids = list(QualitativeScaleSublevel.objects.filter(
            scale_id=instance_id, is_active=True
        ).values_list("id", flat=True))
        counts = {}
        if child_ids:
            counts["escalas por subnivel"] = len(child_ids)
        return counts

    @classmethod
    def deactivate_cascade(cls, instance_id: int) -> int:
        child_ids = list(QualitativeScaleSublevel.objects.filter(
            scale_id=instance_id, is_active=True
        ).values_list("id", flat=True))
        total = 0
        if child_ids:
            total += QualitativeScaleSublevel.objects.filter(id__in=child_ids).update(is_active=False)
        cls.model.objects.filter(pk=instance_id).update(is_active=False)
        return total


class QualitativeScaleSublevelRepository(BaseRepository, QualitativeScaleSublevelRepositoryInterface):
    model = QualitativeScaleSublevel

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.select_related("scale", "sublevel")

    @classmethod
    def get_cascade_counts(cls, instance_id: int) -> dict[str, int]:
        return {}

    @classmethod
    def deactivate_cascade(cls, instance_id: int) -> int:
        cls.model.objects.filter(pk=instance_id).update(is_active=False)
        return 1
