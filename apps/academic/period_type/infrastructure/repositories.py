from django.db import models as db_models, transaction

from apps.core.repositories.base import BaseRepository

from ..domain.repositories import PeriodTypeRepositoryInterface
from .models import PeriodType


class PeriodTypeRepository(BaseRepository, PeriodTypeRepositoryInterface):
    model = PeriodType

    @classmethod
    def get_all(cls, active_only=True, search=None):
        queryset = super().get_all(active_only=active_only)
        if search:
            queryset = queryset.filter(
                db_models.Q(name__icontains=search) | db_models.Q(code__icontains=search)
            )
        return queryset.order_by("name")

    @classmethod
    def get_by_code(cls, code):
        try:
            return cls.model.objects.get(code=code)
        except cls.model.DoesNotExist:
            return None

    @classmethod
    def get_cascade_counts(cls, instance_id: int) -> dict[str, int]:
        from apps.academic.academic_period.infrastructure.models import AcademicPeriod

        period_count = AcademicPeriod.objects.filter(
            period_type_id=instance_id, is_active=True
        ).count()
        counts = {}
        if period_count:
            counts["periodos acad\u00e9micos"] = period_count
        return counts

    @classmethod
    @transaction.atomic
    def deactivate_cascade(cls, instance_id: int) -> int:
        from apps.academic.academic_period.infrastructure.models import AcademicPeriod

        total = AcademicPeriod.objects.filter(
            period_type_id=instance_id, is_active=True
        ).update(is_active=False)
        cls.model.objects.filter(pk=instance_id).update(is_active=False)
        return total
