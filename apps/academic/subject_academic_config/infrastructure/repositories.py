from django.db import models as db_models, transaction

from apps.core.repositories.base import BaseRepository

from ..domain.repositories import SubjectAcademicConfigRepositoryInterface
from .models import SubjectAcademicConfig


class SubjectAcademicConfigRepository(BaseRepository, SubjectAcademicConfigRepositoryInterface):
    model = SubjectAcademicConfig

    @classmethod
    def get_all(cls, active_only=True, search=None):
        queryset = super().get_all(active_only=active_only)
        queryset = queryset.select_related("subject", "academic_grade")
        if search:
            queryset = queryset.filter(
                db_models.Q(subject__name__icontains=search)
                | db_models.Q(academic_grade__name__icontains=search)
            )
        return queryset.order_by("-id")

    @classmethod
    def get_by_subject(cls, subject_id):
        return cls.model.objects.filter(subject_id=subject_id).select_related(
            "academic_grade", "subject"
        )

    @classmethod
    def get_by_grade(cls, academic_grade_id):
        return cls.model.objects.filter(
            academic_grade_id=academic_grade_id
        ).select_related("subject", "academic_grade")

    @classmethod
    def get_cascade_counts(cls, instance_id: int) -> dict[str, int]:
        from apps.academic.subject_offering.infrastructure.models import SubjectOffering

        offering_count = SubjectOffering.objects.filter(
            subject_academic_config_id=instance_id, is_active=True
        ).count()
        counts = {}
        if offering_count:
            counts["ofertas de materia"] = offering_count
        return counts

    @classmethod
    @transaction.atomic
    def deactivate_cascade(cls, instance_id: int) -> int:
        from apps.academic.subject_offering.infrastructure.models import SubjectOffering

        total = SubjectOffering.objects.filter(
            subject_academic_config_id=instance_id, is_active=True
        ).update(is_active=False)
        cls.model.objects.filter(pk=instance_id).update(is_active=False)
        return total
