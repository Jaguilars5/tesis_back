from django.db import transaction

from apps.academic.subject_academic_config.infrastructure.models import SubjectAcademicConfig
from apps.academic.subject_offering.infrastructure.models import SubjectOffering
from apps.core.repositories.base import BaseRepository
from apps.institutions.section.infrastructure.models import Section

from ..domain.repositories import AcademicGradeRepositoryInterface
from .models import AcademicGrade


class AcademicGradeRepository(BaseRepository, AcademicGradeRepositoryInterface):
    model = AcademicGrade

    @classmethod
    def get_all(cls, active_only=True, search=None):
        queryset = super().get_all(active_only=active_only)
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset.order_by("name")

    @classmethod
    def get_by_sublevel(cls, sublevel_id):
        return cls.model.objects.filter(
            academic_sublevel_id=sublevel_id
        ).order_by("name")

    @classmethod
    def get_cascade_counts(cls, instance_id: int) -> dict[str, int]:
        section_ids = Section.objects.filter(academic_grade_id=instance_id, is_active=True).values_list("id", flat=True)
        counts = {}
        section_count = len(section_ids)
        if section_count:
            counts["secciones"] = section_count
        offering_count = SubjectOffering.objects.filter(section_id__in=section_ids, is_active=True).count()
        if offering_count:
            counts["ofertas de materias"] = offering_count
        config_count = SubjectAcademicConfig.objects.filter(academic_grade_id=instance_id, is_active=True).count()
        if config_count:
            counts["configuraciones académicas"] = config_count
        return counts

    @classmethod
    @transaction.atomic
    def deactivate_cascade(cls, instance_id: int) -> int:
        section_ids = list(Section.objects.filter(academic_grade_id=instance_id, is_active=True).values_list("id", flat=True))

        total = 0
        if section_ids:
            total += SubjectOffering.objects.filter(section_id__in=section_ids, is_active=True).update(is_active=False)
            total += Section.objects.filter(id__in=section_ids).update(is_active=False)
        total += SubjectAcademicConfig.objects.filter(academic_grade_id=instance_id, is_active=True).update(is_active=False)

        cls.model.objects.filter(pk=instance_id).update(is_active=False)
        return total
