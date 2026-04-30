from django.db import models
from ..models import Student, Representative, Student_Representative


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
        """Obtener estudiante por DNI"""
        try:
            return cls.model.objects.get(dni=dni)
        except cls.model.DoesNotExist:
            return None

    @classmethod
    def get_by_section(cls, section_id):
        """Obtener estudiantes de una sección"""
        return cls.model.objects.filter(section_id=section_id, active=True).order_by(
            "last_names"
        )

    @classmethod
    def get_by_enrollment_number(cls, enrollment_number):
        """Obtener por número de matrícula"""
        try:
            return cls.model.objects.get(enrollment_number=enrollment_number)
        except cls.model.DoesNotExist:
            return None

    @classmethod
    def search(cls, query):
        """Búsqueda por nombre, DNI o número de matrícula"""
        return (
            cls.model.objects.filter(active=True)
            .filter(
                models.Q(names__icontains=query)
                | models.Q(last_names__icontains=query)
                | models.Q(dni__icontains=query)
                | models.Q(enrollment_number__icontains=query)
            )
            .order_by("last_names", "names")
        )


class RepresentativeRepository(BaseRepository):
    model = Representative

    @classmethod
    def get_by_dni(cls, dni):
        """Obtener representante por DNI"""
        try:
            return cls.model.objects.get(dni=dni)
        except cls.model.DoesNotExist:
            return None

    @classmethod
    def get_by_student(cls, student_id):
        """Obtener todos los representantes de un estudiante"""
        return (
            Student_Representative.objects.filter(student_id=student_id)
            .select_related("representative")
            .order_by("-is_primary")
        )

    @classmethod
    def get_primary_representative(cls, student_id):
        """Obtener el representante principal"""
        relationship = (
            Student_Representative.objects.filter(
                student_id=student_id, is_primary=True
            )
            .select_related("representative")
            .first()
        )
        return relationship.representative if relationship else None

    @classmethod
    def search(cls, query):
        """Búsqueda por nombre o DNI"""
        return (
            cls.model.objects.filter(active=True)
            .filter(
                models.Q(names__icontains=query)
                | models.Q(last_names__icontains=query)
                | models.Q(dni__icontains=query)
            )
            .order_by("last_names", "names")
        )


class StudentRepresentativeRepository(BaseRepository):
    model = Student_Representative

    @classmethod
    def get_by_student(cls, student_id):
        """Obtener todas las relaciones de un estudiante"""
        return cls.model.objects.filter(student_id=student_id).select_related(
            "representative"
        )

    @classmethod
    def get_by_representative(cls, representative_id):
        """Obtener todos los estudiantes de un representante"""
        return cls.model.objects.filter(
            representative_id=representative_id
        ).select_related("student")

    @classmethod
    def get_relationship(cls, student_id, representative_id):
        """Obtener relación específica"""
        try:
            return cls.model.objects.get(
                student_id=student_id, representative_id=representative_id
            )
        except cls.model.DoesNotExist:
            return None
