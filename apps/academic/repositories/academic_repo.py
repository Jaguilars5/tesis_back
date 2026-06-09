from apps.core.repositories.base import BaseRepository
from ..models import (
    AcademicPeriod,
    PeriodType,
    Subject,
    SubjectAcademicConfig,
    SubjectOffering,
    TeacherSubjectSection,
)


class SubjectRepository(BaseRepository):
    model = Subject

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.order_by("name")


class AcademicPeriodRepository(BaseRepository):
    model = AcademicPeriod

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.order_by("-start_date")

    @classmethod
    def get_by_school_year(cls, school_year_id):
        return cls.model.objects.filter(
            school_year_id=school_year_id
        ).order_by("start_date")


class TeacherSubjectSectionRepository(BaseRepository):
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
            qs = qs.filter(subject_offering__school_year_id=school_year_id)
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


class SubjectAcademicConfigRepository(BaseRepository):
    model = SubjectAcademicConfig

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
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


class PeriodTypeRepository(BaseRepository):
    model = PeriodType

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.order_by("name")


class SubjectOfferingRepository(BaseRepository):
    model = SubjectOffering

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.order_by("-id")

    @classmethod
    def get_by_section(cls, section_id, school_year_id=None):
        qs = cls.model.objects.filter(section_id=section_id).select_related(
            "school_year",
            "subject_academic_config__subject",
            "subject_academic_config__academic_grade",
        )
        if school_year_id:
            qs = qs.filter(school_year_id=school_year_id)
        return qs

    @classmethod
    def get_by_school_year(cls, school_year_id):
        return cls.model.objects.filter(school_year_id=school_year_id).select_related(
            "section", "subject_academic_config__subject"
        )
