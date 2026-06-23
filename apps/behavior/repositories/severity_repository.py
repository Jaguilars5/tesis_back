from apps.core.repositories.base import BaseRepository
from apps.behavior.models import Severity


class SeverityRepository(BaseRepository):
    model = Severity

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.order_by("name")

    @classmethod
    def soft_delete(cls, instance):
        instance.is_active = False
        instance.save(update_fields=["is_active"])
        return {"id": instance.pk}
