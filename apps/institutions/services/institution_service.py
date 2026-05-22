from datetime import date
from django.db import transaction
from ..models import School_Year, Classroom
from ..repositories.institution_repo import (
    SchoolYearRepository,
    ClassroomRepository,
)


class InstitutionService:
    """Lógica de negocio para instituciones"""

    # =====================
    # SCHOOL_YEAR METHODS
    # =====================

    @staticmethod
    def create_school_year(name, start_date, end_date):
        if start_date >= end_date:
            raise ValueError("Fecha de inicio debe ser anterior a fecha de cierre")

        existing = School_Year.objects.filter(
            start_date__lte=end_date, end_date__gte=start_date
        ).exists()
        if existing:
            raise ValueError("Conflicto de fechas con otro año escolar")

        school_year = School_Year(
            name=name,
            start_date=start_date,
            end_date=end_date,
        )
        school_year.save()
        return school_year

    @staticmethod
    def get_school_year(school_year_id):
        school_year = SchoolYearRepository.get_by_id(school_year_id)
        if not school_year:
            raise ValueError(f"Año escolar {school_year_id} no encontrado")
        return school_year

    @staticmethod
    def list_school_years(active_only=True):
        query = School_Year.objects.all()
        if active_only:
            query = query.filter(active=True)
        return query.order_by("-start_date")

    @staticmethod
    def get_current_school_year():
        today = date.today()
        school_year = School_Year.objects.filter(
            start_date__lte=today,
            end_date__gte=today,
            active=True,
        ).first()
        if not school_year:
            raise ValueError("No hay año escolar activo")
        return school_year

    @staticmethod
    def update_school_year(school_year_id, **kwargs):
        school_year = InstitutionService.get_school_year(school_year_id)
        if "start_date" in kwargs or "end_date" in kwargs:
            start = kwargs.get("start_date", school_year.start_date)
            end = kwargs.get("end_date", school_year.end_date)
            if start >= end:
                raise ValueError("Fecha de inicio debe ser anterior a fecha de cierre")
        for key, value in kwargs.items():
            if hasattr(school_year, key):
                setattr(school_year, key, value)
        school_year.save()
        return school_year

    @staticmethod
    def deactivate_school_year(school_year_id):
        school_year = InstitutionService.get_school_year(school_year_id)
        school_year.active = False
        school_year.save()
        return school_year

    # =====================
    # CLASSROOM METHODS
    # =====================

    @staticmethod
    def create_classroom(name, room_type_id, capacity):
        if capacity <= 0:
            raise ValueError("Capacidad debe ser mayor a 0")
        classroom = Classroom(name=name, room_type_id=room_type_id, capacity=capacity)
        classroom.save()
        return classroom

    @staticmethod
    def get_classroom(classroom_id):
        classroom = ClassroomRepository.get_by_id(classroom_id)
        if not classroom:
            raise ValueError(f"Aula {classroom_id} no encontrada")
        return classroom

    @staticmethod
    def list_classrooms(active_only=True):
        query = Classroom.objects.all()
        if active_only:
            query = query.filter(active=True)
        return query.order_by("name")

    @staticmethod
    def list_classrooms_by_type(room_type_id):
        return Classroom.objects.filter(
            room_type_id=room_type_id, active=True
        ).order_by("name")

    @staticmethod
    def update_classroom(classroom_id, **kwargs):
        classroom = InstitutionService.get_classroom(classroom_id)
        if "capacity" in kwargs and kwargs["capacity"] <= 0:
            raise ValueError("Capacidad debe ser mayor a 0")
        for key, value in kwargs.items():
            if hasattr(classroom, key):
                setattr(classroom, key, value)
        classroom.save()
        return classroom

    @staticmethod
    def deactivate_classroom(classroom_id):
        classroom = InstitutionService.get_classroom(classroom_id)
        classroom.active = False
        classroom.save()
        return classroom

    @staticmethod
    def get_available_classrooms(capacity_min=None):
        query = Classroom.objects.filter(active=True)
        if capacity_min:
            query = query.filter(capacity__gte=capacity_min)
        return query.order_by("-capacity")
