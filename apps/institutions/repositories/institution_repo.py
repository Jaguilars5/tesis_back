from django.db import models
from ..models import Institution, School_Year, Classroom


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


class InstitutionRepository(BaseRepository):
    model = Institution

    @classmethod
    def get_by_code(cls, code):
        """Obtener institución por código"""
        try:
            return cls.model.objects.get(code=code)
        except cls.model.DoesNotExist:
            return None

    @classmethod
    def search(cls, query):
        """Buscar instituciones por nombre o código"""
        return (
            cls.model.objects.filter(active=True)
            .filter(models.Q(name__icontains=query) | models.Q(code__icontains=query))
            .order_by("name")
        )

    @classmethod
    def get_by_city(cls, city):
        """Obtener instituciones por ciudad"""
        return cls.model.objects.filter(city=city, active=True).order_by("name")


class SchoolYearRepository(BaseRepository):
    model = School_Year

    @classmethod
    def get_by_institution(cls, institution_id):
        """Obtener años escolares de una institución"""
        return cls.model.objects.filter(institution_id=institution_id).order_by(
            "-start_date"
        )

    @classmethod
    def get_active_in_institution(cls, institution_id):
        """Obtener años escolares activos de una institución"""
        return cls.model.objects.filter(
            institution_id=institution_id, active=True
        ).order_by("-start_date")

    @classmethod
    def get_current(cls, institution_id):
        """Obtener año escolar actual de una institución"""
        from datetime import date

        today = date.today()
        return cls.model.objects.filter(
            institution_id=institution_id,
            start_date__lte=today,
            end_date__gte=today,
            active=True,
        ).first()


class ClassroomRepository(BaseRepository):
    model = Classroom

    @classmethod
    def get_by_institution(cls, institution_id):
        """Obtener aulas de una institución"""
        return cls.model.objects.filter(institution_id=institution_id).order_by("name")

    @classmethod
    def get_by_type(cls, institution_id, room_type_id):
        """Obtener aulas por tipo"""
        return cls.model.objects.filter(
            institution_id=institution_id, room_type_id=room_type_id, active=True
        ).order_by("name")

    @classmethod
    def get_by_capacity(cls, institution_id, min_capacity):
        """Obtener aulas con capacidad mínima"""
        return cls.model.objects.filter(
            institution_id=institution_id, capacity__gte=min_capacity, active=True
        ).order_by("-capacity")
