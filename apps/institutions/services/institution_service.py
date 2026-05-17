from datetime import date
from django.db import transaction
from ..models import Institution, School_Year, Classroom
from ..repositories.institution_repo import (
    InstitutionRepository,
    SchoolYearRepository,
    ClassroomRepository,
)


class InstitutionService:
    """Lógica de negocio para instituciones"""

    # =====================
    # INSTITUTION METHODS
    # =====================

    @staticmethod
    def create_institution(name, code, address, city):
        """Crear nueva institución"""
        if InstitutionRepository.get_by_code(code):
            raise ValueError(f"Código de institución '{code}' ya existe")

        institution = Institution(name=name, code=code, address=address, city=city)
        institution.save()
        return institution

    @staticmethod
    def get_institution(institution_id):
        """Obtener institución por ID"""
        institution = InstitutionRepository.get_by_id(institution_id)
        if not institution:
            raise ValueError(f"Institución {institution_id} no encontrada")
        return institution

    @staticmethod
    def get_all_institutions(active_only=True):
        """Listar todas las instituciones"""
        return InstitutionRepository.get_all(active_only=active_only)

    @staticmethod
    def get_institution_details(institution_id):
        """Obtener detalles completos de una institución con años escolares"""
        institution = InstitutionService.get_institution(institution_id)
        return {
            "institution": institution,
            "school_years": School_Year.objects.filter(
                institution=institution
            ).order_by("-start_date"),
            "classrooms": Classroom.objects.filter(institution=institution).order_by(
                "name"
            ),
        }

    @staticmethod
    def update_institution(institution_id, **kwargs):
        """Actualizar institución"""
        institution = InstitutionService.get_institution(institution_id)

        # Validar código único si cambia
        if "code" in kwargs and kwargs["code"] != institution.code:
            if InstitutionRepository.get_by_code(kwargs["code"]):
                raise ValueError(f"Código '{kwargs['code']}' ya existe")

        for key, value in kwargs.items():
            if hasattr(institution, key):
                setattr(institution, key, value)

        institution.save()
        return institution

    @staticmethod
    def deactivate_institution(institution_id):
        """Desactivar institución (soft delete)"""
        institution = InstitutionService.get_institution(institution_id)
        institution.active = False
        institution.save()
        return institution

    @staticmethod
    def search_institutions(query):
        """Buscar instituciones por nombre o código"""
        return InstitutionRepository.search(query)

    # =====================
    # SCHOOL_YEAR METHODS
    # =====================

    @staticmethod
    def create_school_year(institution_id, name, start_date, end_date, academic_regime_id=None):
        """Crear nuevo año escolar"""
        institution = InstitutionService.get_institution(institution_id)

        # Validar fechas
        if start_date >= end_date:
            raise ValueError("Fecha de inicio debe ser anterior a fecha de cierre")

        # Validar no haya conflicto con otros años
        existing = School_Year.objects.filter(
            institution=institution, start_date__lte=end_date, end_date__gte=start_date
        ).exists()

        if existing:
            raise ValueError("Conflicto de fechas con otro año escolar")

        school_year = School_Year(
            institution=institution,
            name=name,
            start_date=start_date,
            end_date=end_date,
            academic_regime_id=academic_regime_id,
        )
        school_year.save()
        return school_year

    @staticmethod
    def get_school_year(school_year_id):
        """Obtener año escolar por ID"""
        school_year = SchoolYearRepository.get_by_id(school_year_id)
        if not school_year:
            raise ValueError(f"Año escolar {school_year_id} no encontrado")
        return school_year

    @staticmethod
    def list_school_years(institution_id, active_only=True):
        """Listar años escolares de una institución"""
        institution = InstitutionService.get_institution(institution_id)
        query = School_Year.objects.filter(institution=institution)

        if active_only:
            query = query.filter(active=True)

        return query.order_by("-start_date")

    @staticmethod
    def get_current_school_year(institution_id):
        """Obtener año escolar actual"""
        institution = InstitutionService.get_institution(institution_id)
        today = date.today()

        school_year = School_Year.objects.filter(
            institution=institution,
            start_date__lte=today,
            end_date__gte=today,
            active=True,
        ).first()

        if not school_year:
            raise ValueError(f"No hay año escolar activo en {institution.name}")

        return school_year

    @staticmethod
    def update_school_year(school_year_id, **kwargs):
        """Actualizar año escolar"""
        school_year = InstitutionService.get_school_year(school_year_id)

        # Validar fechas si se modifican
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
        """Desactivar año escolar"""
        school_year = InstitutionService.get_school_year(school_year_id)
        school_year.active = False
        school_year.save()
        return school_year

    # =====================
    # CLASSROOM METHODS
    # =====================

    @staticmethod
    def create_classroom(institution_id, name, room_type_id, capacity):
        """Crear nueva aula"""
        institution = InstitutionService.get_institution(institution_id)

        if capacity <= 0:
            raise ValueError("Capacidad debe ser mayor a 0")

        classroom = Classroom(
            institution=institution, name=name, room_type_id=room_type_id, capacity=capacity
        )
        classroom.save()
        return classroom

    @staticmethod
    def get_classroom(classroom_id):
        """Obtener aula por ID"""
        classroom = ClassroomRepository.get_by_id(classroom_id)
        if not classroom:
            raise ValueError(f"Aula {classroom_id} no encontrada")
        return classroom

    @staticmethod
    def list_classrooms(institution_id, active_only=True):
        """Listar aulas de una institución"""
        institution = InstitutionService.get_institution(institution_id)
        query = Classroom.objects.filter(institution=institution)

        if active_only:
            query = query.filter(active=True)

        return query.order_by("name")

    @staticmethod
    def list_classrooms_by_type(institution_id, room_type_id):
        """Listar aulas por tipo"""
        institution = InstitutionService.get_institution(institution_id)
        return Classroom.objects.filter(
            institution=institution, room_type_id=room_type_id, active=True
        ).order_by("name")

    @staticmethod
    def update_classroom(classroom_id, **kwargs):
        """Actualizar aula"""
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
        """Desactivar aula"""
        classroom = InstitutionService.get_classroom(classroom_id)
        classroom.active = False
        classroom.save()
        return classroom

    @staticmethod
    def get_available_classrooms(institution_id, capacity_min=None):
        """Obtener aulas disponibles (activas) con capacidad mínima opcional"""
        institution = InstitutionService.get_institution(institution_id)
        query = Classroom.objects.filter(institution=institution, active=True)

        if capacity_min:
            query = query.filter(capacity__gte=capacity_min)

        return query.order_by("-capacity")
