from apps.core.repositories.base import BaseRepository

from ..domain.repositories import QualitativeScaleRepositoryInterface
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


class QualitativeScaleSublevelRepository(BaseRepository):
    model = QualitativeScaleSublevel

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.select_related("scale", "sublevel")
