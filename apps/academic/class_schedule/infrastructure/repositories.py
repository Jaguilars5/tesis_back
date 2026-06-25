import logging
from datetime import date

from django.db import models as db_models

from apps.core.repositories.base import BaseRepository

from ..domain.repositories import ClassScheduleRepositoryInterface
from .models import ClassSchedule

logger = logging.getLogger(__name__)


class ClassScheduleRepository(BaseRepository, ClassScheduleRepositoryInterface):
    model = ClassSchedule

    @classmethod
    def get_all(cls, active_only=True, search=None):
        queryset = super().get_all(active_only=active_only)
        if search:
            queryset = queryset.filter(
                db_models.Q(teacher_subject_section__subject_offering__subject_academic_config__subject__name__icontains=search)
                | db_models.Q(teacher_subject_section__subject_offering__section__parallel__icontains=search)
            )
        return queryset.order_by("day_of_week", "start_time")

    @classmethod
    def get_by_subject_offering(cls, subject_offering_id):
        return cls.model.objects.filter(
            teacher_subject_section__subject_offering_id=subject_offering_id
        )

    @classmethod
    def get_by_teacher(cls, user_id):
        return (
            cls._base_select_related()
            .filter(teacher_subject_section__user_id=user_id)
            .order_by("day_of_week", "start_time")
        )

    @classmethod
    def _base_select_related(cls):
        return cls.model.objects.select_related(
            "teacher_subject_section__subject_offering__section",
            "teacher_subject_section__subject_offering__subject_academic_config__subject",
            "teacher_subject_section__user__person",
        )

    @classmethod
    def get_by_student(cls, student_id):
        from apps.students.models import Enrollment

        section_ids = Enrollment.objects.filter(
            student_id=student_id, enrollment_status="ACT"
        ).values_list("section_id", flat=True)
        if not section_ids:
            return cls.model.objects.none()
        return (
            cls._base_select_related()
            .filter(
                teacher_subject_section__subject_offering__section_id__in=section_ids
            )
            .order_by("day_of_week", "start_time")
        )

    @classmethod
    def get_by_section(cls, section_id):
        return cls._base_select_related().filter(
            teacher_subject_section__subject_offering__section_id=section_id
        ).order_by("day_of_week", "start_time")

    @classmethod
    def get_today_for_teacher(cls, user_id):
        today = date.today()
        day_of_week = today.isoweekday()
        return cls.get_by_teacher(user_id).filter(day_of_week=day_of_week)

    @classmethod
    def check_overlap(
        cls,
        teacher_subject_section_id,
        day_of_week,
        start_time,
        end_time,
        exclude_id=None,
    ):
        qs = cls.model.objects.filter(
            teacher_subject_section_id=teacher_subject_section_id,
            day_of_week=day_of_week,
        )
        if exclude_id:
            qs = qs.exclude(id=exclude_id)
        return qs.filter(
            db_models.Q(start_time__lt=end_time, end_time__gt=start_time)
        ).exists()

    @classmethod
    def get_cascade_counts(cls, instance_id: int) -> dict[str, int]:
        return {}

    @classmethod
    def deactivate_cascade(cls, instance_id: int) -> int:
        cls.model.objects.filter(pk=instance_id).update(is_active=False)
        return 0
