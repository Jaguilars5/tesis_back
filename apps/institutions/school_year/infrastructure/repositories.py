from datetime import date

from django.db import transaction

from apps.academic.academic_period.infrastructure.models import AcademicPeriod
from apps.academic.subject_offering.infrastructure.models import SubjectOffering
from apps.core.repositories.base import BaseRepository
from apps.institutions.section.infrastructure.models import Section

from ..domain.repositories import SchoolYearRepositoryInterface
from .models import SchoolYear


class SchoolYearRepository(BaseRepository, SchoolYearRepositoryInterface):
    model = SchoolYear

    @classmethod
    def get_all(cls, active_only=True, search=None):
        queryset = super().get_all(active_only=active_only)
        return queryset.order_by("-start_date")

    @classmethod
    def get_current(cls):
        today = date.today()
        return cls.model.objects.filter(
            start_date__lte=today,
            end_date__gte=today,
            is_active=True,
        ).first()

    @classmethod
    def has_overlap(cls, start_date, end_date, exclude_id=None):
        queryset = cls.model.objects.filter(
            start_date__lte=end_date, end_date__gte=start_date
        )
        if exclude_id:
            queryset = queryset.exclude(pk=exclude_id)
        return queryset.exists()

    @classmethod
    def get_cascade_counts(cls, instance_id: int) -> dict[str, int]:
        section_ids = Section.objects.filter(school_year_id=instance_id, is_active=True).values_list("id", flat=True)
        counts = {}
        section_count = len(section_ids)
        if section_count:
            counts["secciones"] = section_count
        offering_count = SubjectOffering.objects.filter(section_id__in=section_ids, is_active=True).count()
        if offering_count:
            counts["ofertas de materias"] = offering_count
        period_count = AcademicPeriod.objects.filter(school_year_id=instance_id, is_active=True).count()
        if period_count:
            counts["períodos académicos"] = period_count
        return counts

    @classmethod
    @transaction.atomic
    def deactivate_cascade(cls, instance_id: int) -> int:
        section_ids = list(Section.objects.filter(school_year_id=instance_id, is_active=True).values_list("id", flat=True))
        offering_count = SubjectOffering.objects.filter(section_id__in=section_ids, is_active=True).update(is_active=False)
        section_count = Section.objects.filter(id__in=section_ids).update(is_active=False)
        period_count = AcademicPeriod.objects.filter(school_year_id=instance_id, is_active=True).update(is_active=False)
        cls.model.objects.filter(pk=instance_id).update(is_active=False)
        return section_count + offering_count + period_count
