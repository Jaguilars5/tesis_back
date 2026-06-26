from django.db import transaction

from apps.core.repositories.base import BaseRepository

from ..domain.repositories import AcademicPeriodRepositoryInterface
from .models import AcademicPeriod


class AcademicPeriodRepository(BaseRepository, AcademicPeriodRepositoryInterface):
    model = AcademicPeriod

    @classmethod
    def get_all(cls, active_only=True, search=None):
        queryset = super().get_all(active_only=active_only)
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset.order_by("-start_date")

    @classmethod
    def get_by_school_year(cls, school_year_id):
        return cls.model.objects.filter(
            school_year_id=school_year_id
        ).order_by("start_date")

    @classmethod
    def count_by_school_year_and_period_type(
        cls, school_year_id, period_type_id, exclude_period_id=None
    ):
        qs = cls.model.objects.filter(
            school_year_id=school_year_id,
            period_type_id=period_type_id,
        )
        if exclude_period_id is not None:
            qs = qs.exclude(pk=exclude_period_id)
        return qs.count()

    @classmethod
    def sum_year_weight_by_school_year_and_period_type(
        cls, school_year_id, period_type_id, exclude_period_id=None
    ):
        from django.db.models import Sum

        qs = cls.model.objects.filter(
            school_year_id=school_year_id,
            period_type_id=period_type_id,
            is_regular_period=True,
            year_weight__isnull=False,
        )
        if exclude_period_id is not None:
            qs = qs.exclude(pk=exclude_period_id)
        result = qs.aggregate(total=Sum("year_weight"))
        return result["total"] or 0

    @classmethod
    def has_overlapping_period(
        cls, school_year_id, start_date, end_date, exclude_period_id=None
    ):
        qs = cls.model.objects.filter(
            school_year_id=school_year_id,
            start_date__lte=end_date,
            end_date__gte=start_date,
        )
        if exclude_period_id is not None:
            qs = qs.exclude(pk=exclude_period_id)
        return qs.exists()

    @classmethod
    def get_period_types_in_school_year(cls, school_year_id, exclude_period_id=None):
        qs = cls.model.objects.filter(school_year_id=school_year_id)
        if exclude_period_id is not None:
            qs = qs.exclude(pk=exclude_period_id)
        return list(qs.values_list("period_type_id", flat=True).distinct())

    @classmethod
    def _cascade_active_querysets(cls, instance_id: int):
        """Hijos A1 (con is_active) que se desactivan en cascada al dar de baja el período.

        Los registros A2 (Attendance, ConductIncident) y A4 (PeriodGradeSummary)
        asociados NO se desactivan: no tienen `is_active` (son inmutables / se
        recalculan), por lo que quedan fuera de la cascada de catálogo.
        """
        from apps.grading.evaluation.infrastructure.models import EvaluationBlock

        return {
            "bloques de evaluación": EvaluationBlock.objects.filter(
                academic_period_id=instance_id, is_active=True
            ),
        }

    @classmethod
    def get_cascade_counts(cls, instance_id: int) -> dict[str, int]:
        counts = {}
        for label, queryset in cls._cascade_active_querysets(instance_id).items():
            count = queryset.count()
            if count:
                counts[label] = count
        return counts

    @classmethod
    @transaction.atomic
    def deactivate_cascade(cls, instance_id: int) -> int:
        total = 0
        for queryset in cls._cascade_active_querysets(instance_id).values():
            total += queryset.update(is_active=False)
        cls.model.objects.filter(pk=instance_id).update(is_active=False)
        return total
