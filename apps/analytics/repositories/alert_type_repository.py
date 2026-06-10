from apps.core.repositories.base import BaseRepository
from ..models import AlertType


class AlertTypeRepository(BaseRepository):
    model = AlertType

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.order_by("name")

    @classmethod
    def get_by_code(cls, code):
        return cls.model.objects.get(code=code)
