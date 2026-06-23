from django.db import models
from apps.core.repositories.base import BaseRepository
from ..models import Student, StudentRepresentative


class StudentRepository(BaseRepository):
    model = Student

    @classmethod
    def get_by_dni(cls, dni):
        try:
            return cls.model.objects.get(user__person__document_number=dni)
        except cls.model.DoesNotExist:
            return None

    @classmethod
    def get_by_section(cls, section_id, status_code="ACT"):
        return cls.model.objects.filter(
            enrollments__section_id=section_id,
            enrollments__enrollment_status=status_code,
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


class StudentRepresentativeRepository(BaseRepository):
    model = StudentRepresentative

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.select_related("user__person", "student__user__person")

    @classmethod
    def get_by_student(cls, student_id):
        return cls.model.objects.filter(
            student_id=student_id
        ).select_related("user__person", "student__user__person")

    @classmethod
    def get_by_user(cls, user_id):
        return cls.model.objects.filter(
            user_id=user_id
        ).select_related("student__user__person")

    @classmethod
    def get_relationship(cls, student_id, user_id):
        try:
            return cls.model.objects.select_related(
                "user__person", "student__user__person"
            ).get(student_id=student_id, user_id=user_id)
        except cls.model.DoesNotExist:
            return None
