from apps.core.repositories.base import BaseRepository
from ..models import AbsenceType


class AbsenceTypeRepository(BaseRepository):
    model = AbsenceType

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.order_by("name")
