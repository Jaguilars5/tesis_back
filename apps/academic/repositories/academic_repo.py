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

    @classmethod
    def count_by_school_year_and_period_type(
        cls, school_year_id, period_type_id, exclude_period_id=None
    ):
        qs = cls.model.objects.filter(
            school_year_id=school_year_id,
            period_type_id=period_type_id,
        )
        if exclude_period_id is not None:
            qs = qs.exclude(pk=exclude_period_id)
        return qs.count()

    @classmethod
    def sum_year_weight_by_school_year_and_period_type(
        cls, school_year_id, period_type_id, exclude_period_id=None
    ):
        from django.db.models import Sum

        qs = cls.model.objects.filter(
            school_year_id=school_year_id,
            period_type_id=period_type_id,
            is_regular_period=True,
            year_weight__isnull=False,
        )
        if exclude_period_id is not None:
            qs = qs.exclude(pk=exclude_period_id)
        result = qs.aggregate(total=Sum("year_weight"))
        return result["total"] or 0

    @classmethod
    def has_overlapping_period(
        cls, school_year_id, start_date, end_date, exclude_period_id=None
    ):
        qs = cls.model.objects.filter(
            school_year_id=school_year_id,
            start_date__lte=end_date,
            end_date__gte=start_date,
        )
        if exclude_period_id is not None:
            qs = qs.exclude(pk=exclude_period_id)
        return qs.exists()

    @classmethod
    def get_period_types_in_school_year(cls, school_year_id, exclude_period_id=None):
        qs = cls.model.objects.filter(school_year_id=school_year_id)
        if exclude_period_id is not None:
            qs = qs.exclude(pk=exclude_period_id)
        return list(qs.values_list("period_type_id", flat=True).distinct())


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
            qs = qs.filter(subject_offering__section__school_year_id=school_year_id)
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
            user_id=user_id,
            subject_offering_id=subject_offering_id,
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

    @classmethod
    def get_by_code(cls, code):
        try:
            return cls.model.objects.get(code=code)
        except cls.model.DoesNotExist:
            return None


class SubjectOfferingRepository(BaseRepository):
    model = SubjectOffering

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
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
        return cls.model.objects.filter(section__school_year_id=school_year_id).select_related(
            "section", "subject_academic_config__subject"
        )
