from ..models import SystemConfig
from apps.core.repositories.base import BaseRepository


class ConfigRepository(BaseRepository):
    model = SystemConfig

    @classmethod
    def get_all(cls, active_only=True):
        return cls.model.objects.all().order_by("key")

    @classmethod
    def get_by_key(cls, key):
        try:
            return cls.model.objects.get(key=key)
        except cls.model.DoesNotExist:
            return None

    @classmethod
    def get_or_create(cls, key, defaults=None):
        obj, created = cls.model.objects.get_or_create(
            key=key,
            defaults=defaults or {},
        )
        return obj, created
