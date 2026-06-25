from django.db import models as db_models, transaction

from apps.core.repositories.base import BaseRepository

from ..domain.repositories import TeacherSubjectSectionRepositoryInterface
from .models import TeacherSubjectSection


class TeacherSubjectSectionRepository(
    BaseRepository, TeacherSubjectSectionRepositoryInterface
):
    model = TeacherSubjectSection

    @classmethod
    def _base_select_related(cls):
        return cls.model.objects.select_related(
            "user__person",
            "subject_offering__section__school_year",
            "subject_offering__section__academic_grade",
            "subject_offering__subject_academic_config__subject",
            "subject_offering__subject_academic_config__academic_grade",
        )

    @classmethod
    def get_all(cls, active_only=True, search=None):
        queryset = cls._base_select_related()
        if active_only and hasattr(cls.model, "is_active"):
            queryset = queryset.filter(is_active=True)
        if search:
            queryset = queryset.filter(
                db_models.Q(user__person__names__icontains=search)
                | db_models.Q(user__person__last_names__icontains=search)
                | db_models.Q(subject_offering__section__parallel__icontains=search)
                | db_models.Q(subject_offering__subject_academic_config__subject__name__icontains=search)
            )
        return queryset.order_by("-id")

    @classmethod
    def get_by_user(cls, user_id, school_year_id=None):
        qs = cls.model.objects.filter(user_id=user_id).select_related(
            "subject_offering__subject_academic_config__subject",
            "subject_offering__section",
        )
        if school_year_id:
            qs = qs.filter(
                subject_offering__section__school_year_id=school_year_id
            )
        return qs

    @classmethod
    def get_by_section(cls, section_id):
        return cls.model.objects.filter(
            subject_offering__section_id=section_id
        ).select_related(
            "user__person",
            "subject_offering__subject_academic_config__subject",
        )

    @classmethod
    def get_by_subject_offering(cls, subject_offering_id):
        return cls.model.objects.filter(
            subject_offering_id=subject_offering_id
        ).select_related("user__person")

    @classmethod
    def get_by_subject(cls, subject_id):
        return cls.model.objects.filter(
            subject_offering__subject_academic_config__subject_id=subject_id
        ).select_related(
            "user__person",
            "subject_offering__subject_academic_config__subject",
        )

    @classmethod
    def exists_by_user_and_offering(cls, user_id, subject_offering_id):
        return cls.model.objects.filter(
            user_id=user_id, subject_offering_id=subject_offering_id
        ).exists()

    @classmethod
    def filter_by_assignments(cls, user_id=None, subject_offering_id=None):
        qs = cls._base_select_related()
        if user_id:
            qs = qs.filter(user_id=user_id)
        if subject_offering_id:
            qs = qs.filter(subject_offering_id=subject_offering_id)
        return qs

    @classmethod
    def get_cascade_counts(cls, instance_id: int) -> dict[str, int]:
        from apps.academic.class_schedule.infrastructure.models import ClassSchedule

        schedule_count = ClassSchedule.objects.filter(
            teacher_subject_section_id=instance_id, is_active=True
        ).count()
        counts = {}
        if schedule_count:
            counts["horarios"] = schedule_count
        return counts

    @classmethod
    @transaction.atomic
    def deactivate_cascade(cls, instance_id: int) -> int:
        from apps.academic.class_schedule.infrastructure.models import ClassSchedule

        total = ClassSchedule.objects.filter(
            teacher_subject_section_id=instance_id, is_active=True
        ).update(is_active=False)
        cls.model.objects.filter(pk=instance_id).update(is_active=False)
        return total
