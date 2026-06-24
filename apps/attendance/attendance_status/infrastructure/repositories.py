from apps.core.repositories.base import BaseRepository

from ..domain.repositories import AttendanceStatusRepositoryInterface
from .models import AttendanceStatus


class AttendanceStatusRepository(BaseRepository, AttendanceStatusRepositoryInterface):
    model = AttendanceStatus

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.order_by("name")
