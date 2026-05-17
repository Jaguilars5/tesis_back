from django.db import models
from ..models import Student, Student_Representative


class BaseRepository:
    model = None

    @classmethod
    def get_all(cls, active_only=True):
        queryset = cls.model.objects.all()
        if active_only and hasattr(cls.model, "active"):
            queryset = queryset.filter(active=True)
        return queryset

    @classmethod
    def get_by_id(cls, pk):
        try:
            return cls.model.objects.get(pk=pk)
        except cls.model.DoesNotExist:
            return None


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
            enrollment__section_id=section_id,
            enrollment__enrollment_status__code=status_code,
            active=True,
        ).distinct()

    @classmethod
    def search(cls, query):
        return (
            cls.model.objects.filter(active=True)
            .filter(
                models.Q(person__names__icontains=query)
                | models.Q(person__last_names__icontains=query)
                | models.Q(person__document_number__icontains=query)
                | models.Q(student_code__icontains=query)
            )
            .order_by("person__last_names", "person__names")
        )


class StudentRepresentativeRepository(BaseRepository):
    model = Student_Representative

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
