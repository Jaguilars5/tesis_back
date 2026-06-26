from django.db import transaction

from apps.core.repositories.base import BaseRepository

from ..domain.repositories import AbsenceTypeRepositoryInterface
from .models import AbsenceType


class AbsenceTypeRepository(BaseRepository, AbsenceTypeRepositoryInterface):
    model = AbsenceType

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.order_by("name")

    @classmethod
    def code_exists(cls, code, exclude_id=None):
        qs = cls.model.objects.filter(code=code)
        if exclude_id is not None:
            qs = qs.exclude(pk=exclude_id)
        return qs.exists()

    @classmethod
    def get_cascade_counts(cls, instance_id: int) -> dict[str, int]:
        return {}

    @classmethod
    @transaction.atomic
    def deactivate_cascade(cls, instance_id: int) -> int:
        cls.model.objects.filter(pk=instance_id).update(is_active=False)
        return 0
