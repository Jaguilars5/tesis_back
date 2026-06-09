from django.db import models
from apps.core.repositories.base import BaseRepository
from ..models import Enrollment


class EnrollmentRepository(BaseRepository):
    model = Enrollment

    @classmethod
    def get_active_by_student(cls, student):
        return cls.model.objects.filter(
            student=student,
            enrollment_status__code="ACT",
        ).select_related("section", "enrollment_status").first()

    @classmethod
    def get_by_section(cls, section, status_code=None):
        qs = cls.model.objects.filter(section=section).select_related(
            "student__person", "enrollment_status"
        )
        if status_code:
            qs = qs.filter(enrollment_status__code=status_code)
        return qs

    @classmethod
    def get_by_school_year(cls, school_year):
        return cls.model.objects.filter(
            section__school_year=school_year
        ).select_related("student__person", "section", "enrollment_status")

    @classmethod
    def get_students_by_section(cls, section, status_code="ACT"):
        return cls.model.objects.filter(
            section=section,
            enrollment_status__code=status_code,
        ).select_related("student__person")

    @classmethod
    def count_active_in_section(cls, section):
        return cls.model.objects.filter(
            section=section,
            enrollment_status__code="ACT",
        ).count()

    @classmethod
    def has_active_enrollment(cls, student):
        return cls.model.objects.filter(
            student=student,
            enrollment_status__code="ACT",
        ).exists()
