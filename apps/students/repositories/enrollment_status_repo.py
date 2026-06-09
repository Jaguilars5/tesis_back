from apps.core.repositories.base import BaseRepository
from ..models import EnrollmentStatus


class EnrollmentStatusRepository(BaseRepository):
    model = EnrollmentStatus

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.order_by("name")

    @classmethod
    def get_or_create(cls, code, defaults=None):
        obj, _ = cls.model.objects.get_or_create(code=code, defaults=defaults or {})
        return obj
