from django.db import transaction

from apps.academic.subject_academic_config.infrastructure.models import SubjectAcademicConfig
from apps.academic.subject_offering.infrastructure.models import SubjectOffering
from apps.core.repositories.base import BaseRepository
from apps.grading.qualitative_scale.infrastructure.models import QualitativeScaleSublevel
from apps.institutions.academic_grade.infrastructure.models import AcademicGrade
from apps.institutions.academic_sublevel.infrastructure.models import AcademicSublevel
from apps.institutions.section.infrastructure.models import Section

from ..domain.repositories import AcademicLevelRepositoryInterface
from .models import AcademicLevel


class AcademicLevelRepository(BaseRepository, AcademicLevelRepositoryInterface):
    model = AcademicLevel

    @classmethod
    def get_all(cls, active_only=True, search=None):
        queryset = super().get_all(active_only=active_only)
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset.order_by("name")

    @classmethod
    def get_cascade_counts(cls, instance_id: int) -> dict[str, int]:
        sublevel_ids = AcademicSublevel.objects.filter(academic_level_id=instance_id, is_active=True).values_list("id", flat=True)
        counts = {}
        sublevel_count = len(sublevel_ids)
        if sublevel_count:
            counts["subniveles"] = sublevel_count
        grade_ids = AcademicGrade.objects.filter(academic_sublevel_id__in=sublevel_ids, is_active=True).values_list("id", flat=True)
        grade_count = len(grade_ids)
        if grade_count:
            counts["grados"] = grade_count
        section_ids = Section.objects.filter(academic_grade_id__in=grade_ids, is_active=True).values_list("id", flat=True)
        section_count = len(section_ids)
        if section_count:
            counts["secciones"] = section_count
        offering_count = SubjectOffering.objects.filter(section_id__in=section_ids, is_active=True).count()
        if offering_count:
            counts["ofertas de materias"] = offering_count
        config_count = SubjectAcademicConfig.objects.filter(academic_grade_id__in=grade_ids, is_active=True).count()
        if config_count:
            counts["configuraciones académicas"] = config_count
        scale_count = QualitativeScaleSublevel.objects.filter(sublevel_id__in=sublevel_ids, is_active=True).count()
        if scale_count:
            counts["escalas cualitativas"] = scale_count
        return counts

    @classmethod
    @transaction.atomic
    def deactivate_cascade(cls, instance_id: int) -> int:
        sublevel_ids = list(AcademicSublevel.objects.filter(academic_level_id=instance_id, is_active=True).values_list("id", flat=True))
        grade_ids = list(AcademicGrade.objects.filter(academic_sublevel_id__in=sublevel_ids, is_active=True).values_list("id", flat=True))
        section_ids = list(Section.objects.filter(academic_grade_id__in=grade_ids, is_active=True).values_list("id", flat=True))

        total = 0
        if section_ids:
            total += SubjectOffering.objects.filter(section_id__in=section_ids, is_active=True).update(is_active=False)
            total += Section.objects.filter(id__in=section_ids).update(is_active=False)
        if grade_ids:
            total += SubjectAcademicConfig.objects.filter(academic_grade_id__in=grade_ids, is_active=True).update(is_active=False)
            total += AcademicGrade.objects.filter(id__in=grade_ids).update(is_active=False)
        if sublevel_ids:
            total += QualitativeScaleSublevel.objects.filter(sublevel_id__in=sublevel_ids, is_active=True).update(is_active=False)
            total += AcademicSublevel.objects.filter(id__in=sublevel_ids).update(is_active=False)

        cls.model.objects.filter(pk=instance_id).update(is_active=False)
        return total
