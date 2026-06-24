from apps.core.repositories.base import BaseRepository

from ..domain.repositories import TeacherSubjectSectionRepositoryInterface
from .models import TeacherSubjectSection


class TeacherSubjectSectionRepository(
    BaseRepository, TeacherSubjectSectionRepositoryInterface
):
    model = TeacherSubjectSection

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
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
        qs = cls.model.objects.all().select_related(
            "user__person",
            "subject_offering__subject_academic_config__subject",
        )
        if user_id:
            qs = qs.filter(user_id=user_id)
        if subject_offering_id:
            qs = qs.filter(subject_offering_id=subject_offering_id)
        return qs
