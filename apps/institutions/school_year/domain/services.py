from django.db import transaction

from ..infrastructure.repositories import SchoolYearRepository


class SchoolYearService:
    """L\u00f3gica de negocio para a\u00f1os escolares."""

    repository = SchoolYearRepository

    @classmethod
    @transaction.atomic
    def create_school_year(cls, start_date, end_date):
        if start_date >= end_date:
            raise ValueError("Fecha de inicio debe ser anterior a fecha de cierre")
        if cls.repository.has_overlap(start_date, end_date):
            raise ValueError("Conflicto de fechas con otro a\u00f1o escolar")
        return cls.repository.create(start_date=start_date, end_date=end_date)

    @classmethod
    def get_school_year(cls, pk):
        obj = cls.repository.get_by_id(pk)
        if not obj:
            raise ValueError(f"A\u00f1o escolar {pk} no encontrado")
        return obj

    @classmethod
    def list_school_years(cls, active_only=True, search=None):
        return cls.repository.get_all(active_only=active_only, search=search)

    @classmethod
    def get_current_school_year(cls):
        obj = cls.repository.get_current()
        if not obj:
            raise ValueError("No hay a\u00f1o escolar activo")
        return obj

    @classmethod
    def update_school_year(cls, pk, **kwargs):
        obj = cls.get_school_year(pk)
        if "start_date" in kwargs or "end_date" in kwargs:
            start = kwargs.get("start_date", obj.start_date)
            end = kwargs.get("end_date", obj.end_date)
            if start >= end:
                raise ValueError("Fecha de inicio debe ser anterior a fecha de cierre")
        allowed = {"start_date", "end_date", "is_active"}
        clean = {k: v for k, v in kwargs.items() if k in allowed}
        return cls.repository.update(pk, **clean)

    @classmethod
    def deactivate_school_year(cls, pk):
        obj = cls.get_school_year(pk)
        return cls.repository.update(pk, is_active=False)
