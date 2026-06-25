from django.db import models as db_models, transaction

from apps.core.repositories.base import BaseRepository

from ..domain.repositories import SubjectOfferingRepositoryInterface
from .models import SubjectOffering


class SubjectOfferingRepository(BaseRepository, SubjectOfferingRepositoryInterface):
    model = SubjectOffering

    @classmethod
    def get_all(cls, active_only=True, search=None):
        queryset = super().get_all(active_only=active_only)
        queryset = queryset.select_related(
            "section__school_year",
            "subject_academic_config__subject",
            "subject_academic_config__academic_grade",
        )
        if search:
            queryset = queryset.filter(
                db_models.Q(subject_academic_config__subject__name__icontains=search)
                | db_models.Q(section__parallel__icontains=search)
            )
        return queryset.order_by("-id")

    @classmethod
    def get_by_section(cls, section_id, school_year_id=None):
        qs = cls.model.objects.filter(section_id=section_id).select_related(
            "section__school_year",
            "subject_academic_config__subject",
            "subject_academic_config__academic_grade",
        )
        if school_year_id:
            qs = qs.filter(section__school_year_id=school_year_id)
        return qs

    @classmethod
    def get_by_school_year(cls, school_year_id):
        return cls.model.objects.filter(
            section__school_year_id=school_year_id
        ).select_related(
            "section", "subject_academic_config__subject"
        )

    @classmethod
    def get_cascade_counts(cls, instance_id: int) -> dict[str, int]:
        from apps.academic.teacher_subject_section.infrastructure.models import TeacherSubjectSection

        tss_count = TeacherSubjectSection.objects.filter(
            subject_offering_id=instance_id, is_active=True
        ).count()
        counts = {}
        if tss_count:
            counts["asignaciones docente-materia"] = tss_count
        return counts

    @classmethod
    @transaction.atomic
    def deactivate_cascade(cls, instance_id: int) -> int:
        from apps.academic.teacher_subject_section.infrastructure.models import TeacherSubjectSection

        total = TeacherSubjectSection.objects.filter(
            subject_offering_id=instance_id, is_active=True
        ).update(is_active=False)
        cls.model.objects.filter(pk=instance_id).update(is_active=False)
        return total
