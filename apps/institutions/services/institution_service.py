from datetime import date
from django.db import transaction
from ..repositories.institution_repo import SchoolYearRepository


class InstitutionService:
    """Lógica de negocio para instituciones"""

    # =====================
    # SCHOOL_YEAR METHODS
    # =====================

    @staticmethod
    def create_school_year(start_date, end_date):
        if start_date >= end_date:
            raise ValueError("Fecha de inicio debe ser anterior a fecha de cierre")

        if SchoolYearRepository.has_overlap(start_date, end_date):
            raise ValueError("Conflicto de fechas con otro año escolar")

        school_year = SchoolYearRepository.create(
            start_date=start_date,
            end_date=end_date,
        )
        return school_year

    @staticmethod
    def get_school_year(school_year_id):
        school_year = SchoolYearRepository.get_by_id(school_year_id)
        if not school_year:
            raise ValueError(f"Año escolar {school_year_id} no encontrado")
        return school_year

    @staticmethod
    def list_school_years(active_only=True):
        return SchoolYearRepository.get_all(active_only=active_only)

    @staticmethod
    def get_current_school_year():
        school_year = SchoolYearRepository.get_current()
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
        school_year.is_active = False
        school_year.save()
        return school_year
