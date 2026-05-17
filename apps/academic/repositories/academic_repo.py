from django.db import models
from ..models import (
    Academic_Period, Section, Subject, SubjectAcademicConfig, SubjectOffering,
    Teacher_Subject_Section, Timing_Regime,
)


class BaseRepository:
    model = None

    @classmethod
    def get_all(cls, active_only=True):
        queryset = cls.model.objects.all()
        if active_only and hasattr(cls.model, 'active'):
            queryset = queryset.filter(active=True)
        return queryset

    @classmethod
    def get_by_id(cls, pk):
        try:
            return cls.model.objects.get(pk=pk)
        except cls.model.DoesNotExist:
            return None


class SectionRepository(BaseRepository):
    model = Section

    @classmethod
    def get_by_school_year(cls, school_year_id):
        return cls.model.objects.filter(
            school_year_id=school_year_id
        ).select_related("academic_grade__academic_level").order_by(
            "academic_grade__sequence_order", "parallel"
        )

    @classmethod
    def get_by_grade(cls, academic_grade_id):
        return cls.model.objects.filter(
            academic_grade_id=academic_grade_id
        ).select_related("school_year", "academic_grade")


class SubjectRepository(BaseRepository):
    model = Subject


class AcademicPeriodRepository(BaseRepository):
    model = Academic_Period

    @classmethod
    def get_by_school_year(cls, school_year_id):
        return cls.model.objects.filter(
            school_year_id=school_year_id, active=True
        ).order_by("start_date")


class TimingRegimeRepository(BaseRepository):
    model = Timing_Regime

    @classmethod
    def get_by_institution(cls, institution_id):
        return cls.model.objects.filter(
            institution_id=institution_id, active=True
        )


class TeacherSubjectSectionRepository(BaseRepository):
    model = Teacher_Subject_Section

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
    def get_by_subject(cls, subject_id):
        return cls.model.objects.filter(subject_id=subject_id).select_related(
            "academic_grade", "subject"
        )

    @classmethod
    def get_by_grade(cls, academic_grade_id):
        return cls.model.objects.filter(
            academic_grade_id=academic_grade_id
        ).select_related("subject", "academic_grade")


class SubjectOfferingRepository(BaseRepository):
    model = SubjectOffering

    @classmethod
    def get_by_section(cls, section_id, school_year_id=None):
        qs = cls.model.objects.filter(section_id=section_id).select_related(
            "school_year", "subject_academic_config__subject",
            "subject_academic_config__academic_grade",
        )
        if school_year_id:
            qs = qs.filter(school_year_id=school_year_id)
        return qs

    @classmethod
    def get_by_school_year(cls, school_year_id):
        return cls.model.objects.filter(
            school_year_id=school_year_id
        ).select_related(
            "section", "subject_academic_config__subject"
        )
