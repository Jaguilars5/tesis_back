from django.db import models

from apps.core.repositories.base import BaseRepository

from ..domain.repositories import (
    EnrollmentRepositoryInterface,
    StudentRepresentativeRepositoryInterface,
    StudentRepositoryInterface,
)
from .models import Enrollment, Kinship, SpecialNeedsType, Student, StudentRepresentative, WithdrawalReason


class StudentRepository(BaseRepository, StudentRepositoryInterface):
    model = Student

    @classmethod
    def get_all(cls, active_only=True):
        return super().get_all(active_only=active_only).select_related("user__person").order_by("user__person__last_names")

    @classmethod
    def get_by_dni(cls, dni):
        try:
            return cls.model.objects.get(user__person__document_number=dni)
        except cls.model.DoesNotExist:
            return None

    @classmethod
    def get_by_section(cls, section_id):
        return cls.model.objects.filter(
            enrollments__section_id=section_id,
            enrollments__enrollment_status="ACT",
            is_active=True,
        ).distinct()

    @classmethod
    def search(cls, query):
        return (
            cls.model.objects.filter(is_active=True)
            .filter(
                models.Q(user__person__names__icontains=query)
                | models.Q(user__person__last_names__icontains=query)
                | models.Q(user__person__document_number__icontains=query)
                | models.Q(student_code__icontains=query)
            )
            .order_by("user__person__last_names", "user__person__names")
        )


class StudentRepresentativeRepository(BaseRepository, StudentRepresentativeRepositoryInterface):
    model = StudentRepresentative

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.select_related("user__person", "student__user__person", "kinship")

    @classmethod
    def get_by_student(cls, student_id):
        return (
            cls.model.objects.filter(student_id=student_id)
            .select_related("user__person", "student__user__person", "kinship")
            .order_by("-is_primary", "-created_at")
        )

    @classmethod
    def get_by_person(cls, user_id):
        return cls.model.objects.filter(user_id=user_id, is_active=True).select_related(
            "student__user__person", "kinship"
        )

    @classmethod
    def get_relationship(cls, student_id, user_id):
        try:
            return cls.model.objects.select_related(
                "user__person", "student__user__person", "kinship"
            ).get(student_id=student_id, user_id=user_id)
        except cls.model.DoesNotExist:
            return None


class EnrollmentRepository(BaseRepository, EnrollmentRepositoryInterface):
    model = Enrollment

    @classmethod
    def get_all(cls, active_only=True):
        return super().get_all(active_only=active_only).select_related("student__user__person", "section")

    @classmethod
    def get_active_by_student(cls, student_id):
        from .models import EnrollmentStatusChoices

        return cls.model.objects.filter(
            student_id=student_id,
            enrollment_status=EnrollmentStatusChoices.ACTIVE,
            section__school_year__is_active=True,
        ).select_related("section").first()

    @classmethod
    def get_by_section(cls, section_id):
        return cls.model.objects.filter(section_id=section_id, is_active=True).select_related(
            "student__user__person"
        )

    @classmethod
    def get_by_school_year(cls, school_year_id):
        return cls.model.objects.filter(
            section__school_year_id=school_year_id, is_active=True
        ).select_related("student__user__person", "section")

    @classmethod
    def get_students_by_section(cls, section_id, status_code="ACT"):
        return cls.model.objects.filter(
            section_id=section_id,
            enrollment_status=status_code,
        ).select_related("student__user__person")

    @classmethod
    def count_active_in_section(cls, section_id):
        from .models import EnrollmentStatusChoices

        return cls.model.objects.filter(
            section_id=section_id,
            enrollment_status=EnrollmentStatusChoices.ACTIVE,
        ).count()

    @classmethod
    def has_active_enrollment(cls, student_id):
        from .models import EnrollmentStatusChoices

        return cls.model.objects.filter(
            student_id=student_id,
            enrollment_status=EnrollmentStatusChoices.ACTIVE,
        ).exists()

    @classmethod
    def get_by_representative(cls, user):
        return cls.model.objects.filter(
            student__representatives_set__user=user,
            section__school_year__is_active=True,
        ).select_related("student__user__person", "section").distinct()
