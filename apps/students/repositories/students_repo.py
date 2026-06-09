from django.db import models
from apps.core.repositories.base import BaseRepository
from ..models import Student, StudentRepresentative


class StudentRepository(BaseRepository):
    model = Student

    @classmethod
    def get_by_dni(cls, dni):
        try:
            return cls.model.objects.get(person__document_number=dni)
        except cls.model.DoesNotExist:
            return None

    @classmethod
    def get_by_section(cls, section_id, status_code="ACT"):
        return cls.model.objects.filter(
            enrollments__section_id=section_id,
            enrollments__enrollment_status__code=status_code,
            is_active=True,
        ).distinct()

    @classmethod
    def search(cls, query):
        return (
            cls.model.objects.filter(is_active=True)
            .filter(
                models.Q(person__names__icontains=query)
                | models.Q(person__last_names__icontains=query)
                | models.Q(person__document_number__icontains=query)
                | models.Q(student_code__icontains=query)
            )
            .order_by("person__last_names", "person__names")
        )


class StudentRepresentativeRepository(BaseRepository):
    model = StudentRepresentative

    @classmethod
    def get_by_student(cls, student_id):
        return cls.model.objects.filter(student_id=student_id).select_related("person")

    @classmethod
    def get_by_person(cls, person_id):
        return cls.model.objects.filter(person_id=person_id).select_related("student")

    @classmethod
    def get_relationship(cls, student_id, person_id):
        try:
            return cls.model.objects.get(
                student_id=student_id, person_id=person_id
            )
        except cls.model.DoesNotExist:
            return None
