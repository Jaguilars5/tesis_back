from django.db import models
from ..models import Enrollment


class EnrollmentRepository:
    @staticmethod
    def get_active_by_student(student):
        return Enrollment.objects.filter(
            student=student,
            enrollment_status__code="ACT",
        ).select_related("section", "enrollment_status").first()

    @staticmethod
    def get_by_section(section, status_code=None):
        qs = Enrollment.objects.filter(section=section).select_related(
            "student__person", "enrollment_status"
        )
        if status_code:
            qs = qs.filter(enrollment_status__code=status_code)
        return qs

    @staticmethod
    def get_by_school_year(school_year):
        return Enrollment.objects.filter(
            section__school_year=school_year
        ).select_related("student__person", "section", "enrollment_status")

    @staticmethod
    def get_students_by_section(section, status_code="ACT"):
        return Enrollment.objects.filter(
            section=section,
            enrollment_status__code=status_code,
        ).select_related("student__person")

    @staticmethod
    def count_active_in_section(section):
        return Enrollment.objects.filter(
            section=section,
            enrollment_status__code="ACT",
        ).count()

    @staticmethod
    def has_active_enrollment(student):
        return Enrollment.objects.filter(
            student=student,
            enrollment_status__code="ACT",
        ).exists()
