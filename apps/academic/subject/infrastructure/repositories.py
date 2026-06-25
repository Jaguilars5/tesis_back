from django.db import models as db_models, transaction

from apps.core.repositories.base import BaseRepository

from ..domain.repositories import SubjectRepositoryInterface
from .models import Subject


class SubjectRepository(BaseRepository, SubjectRepositoryInterface):
    model = Subject

    @classmethod
    def get_all(cls, active_only=True, search=None):
        queryset = super().get_all(active_only=active_only)
        if search:
            queryset = queryset.filter(
                db_models.Q(name__icontains=search) | db_models.Q(code__icontains=search)
            )
        return queryset.order_by("name")

    @classmethod
    def get_cascade_counts(cls, instance_id: int) -> dict[str, int]:
        from apps.academic.subject_academic_config.infrastructure.models import SubjectAcademicConfig

        config_count = SubjectAcademicConfig.objects.filter(
            subject_id=instance_id, is_active=True
        ).count()
        counts = {}
        if config_count:
            counts["configuraciones acad\u00e9micas"] = config_count
        return counts

    @classmethod
    @transaction.atomic
    def deactivate_cascade(cls, instance_id: int) -> int:
        from apps.academic.subject_academic_config.infrastructure.models import SubjectAcademicConfig

        total = SubjectAcademicConfig.objects.filter(
            subject_id=instance_id, is_active=True
        ).update(is_active=False)
        cls.model.objects.filter(pk=instance_id).update(is_active=False)
        return total
