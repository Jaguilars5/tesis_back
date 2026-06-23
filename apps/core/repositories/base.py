"""Repositorio base unificado para todas las apps."""

from django.db import models
from django.utils import timezone


class BaseRepository:
    """
    Repositorio base con operaciones CRUD genéricas.
    Todas las apps deben heredar de aquí, NO definir su propio BaseRepository.
    """
    model = None

    @classmethod
    def get_all(cls, active_only=True):
        queryset = cls.model.objects.all()
        if active_only and hasattr(cls.model, "is_active"):
            queryset = queryset.filter(is_active=True)
        return queryset

    @classmethod
    def get_by_id(cls, pk):
        try:
            return cls.model.objects.get(pk=pk)
        except cls.model.DoesNotExist:
            return None

    @classmethod
    def get_by_uuid(cls, uuid):
        try:
            return cls.model.objects.get(uuid=uuid)
        except (cls.model.DoesNotExist, ValueError):
            return None

    @classmethod
    def filter(cls, **filters):
        return cls.model.objects.filter(**filters)

    @classmethod
    def first(cls, **filters):
        return cls.model.objects.filter(**filters).first()

    @classmethod
    def exists(cls, **filters):
        return cls.model.objects.filter(**filters).exists()

    @classmethod
    def count(cls, **filters):
        return cls.model.objects.filter(**filters).count()

    @classmethod
    def create(cls, **data):
        now = timezone.now()
        data.setdefault("created_at", now)
        data["updated_at"] = now
        return cls.model.objects.create(**data)

    @classmethod
    def get_or_create(cls, defaults=None, **lookup):
        return cls.model.objects.get_or_create(defaults=defaults, **lookup)

    @classmethod
    def update(cls, pk, **data):
        data["updated_at"] = timezone.now()
        cls.model.objects.filter(pk=pk).update(**data)
        return cls.get_by_id(pk)

    @classmethod
    def delete(cls, pk):
        return cls.model.objects.filter(pk=pk).delete()
