from django.db import models
from apps.core.repositories.base import BaseRepository
from ..models import Enrollment


class EnrollmentRepository(BaseRepository):
    model = Enrollment

    @classmethod
    def get_active_by_student(cls, student):
        return cls.model.objects.filter(
            student=student,
            enrollment_status="ACT",
        ).select_related("section").first()

    @classmethod
    def get_by_section(cls, section, status_code=None):
        qs = cls.model.objects.filter(section=section).select_related(
            "student__user__person",
        )
        if status_code:
            qs = qs.filter(enrollment_status=status_code)
        return qs

    @classmethod
    def get_by_school_year(cls, school_year):
        return cls.model.objects.filter(
            section__school_year=school_year
        ).select_related("student__user__person", "section")

    @classmethod
    def get_students_by_section(cls, section, status_code="ACT"):
        return cls.model.objects.filter(
            section=section,
            enrollment_status=status_code,
        ).select_related("student__user__person")

    @classmethod
    def count_active_in_section(cls, section):
        return cls.model.objects.filter(
            section=section,
            enrollment_status="ACT",
        ).count()

    @classmethod
    def has_active_enrollment(cls, student):
        return cls.model.objects.filter(
            student=student,
            enrollment_status="ACT",
        ).exists()

    @classmethod
    def has_enrollment_in_school_year(cls, student, school_year):
        return cls.model.objects.filter(
            student=student,
            section__school_year=school_year,
        ).exists()

    @classmethod
    def get_active_by_student_excluding(cls, student, exclude_id):
        return cls.model.objects.filter(
            student=student,
            enrollment_status="ACT",
        ).exclude(id=exclude_id).first()
