from django.db import transaction

from ..application import validators
from ..infrastructure.repositories import SchoolYearRepository


class SchoolYearService:
    """L\u00f3gica de negocio para años escolares."""

    repository = SchoolYearRepository

    @classmethod
    def _validate_or_raise(cls, start_date, end_date):
        errors = validators.run_all_validators(start_date, end_date)
        if errors:
            raise ValueError(errors)

    @classmethod
    @transaction.atomic
    def create_school_year(cls, start_date, end_date):
        cls._validate_or_raise(start_date, end_date)
        if cls.repository.has_overlap(start_date, end_date):
            raise ValueError({"school_year": "Conflicto de fechas con otro año escolar"})
        return cls.repository.create(start_date=start_date, end_date=end_date)

    @classmethod
    def get_school_year(cls, pk):
        obj = cls.repository.get_by_id(pk)
        if not obj:
            raise ValueError(f"Año escolar {pk} no encontrado")
        return obj

    @classmethod
    def list_school_years(cls, active_only=True, search=None):
        return cls.repository.get_all(active_only=active_only, search=search)

    @classmethod
    def get_current_school_year(cls):
        obj = cls.repository.get_current()
        if not obj:
            raise ValueError("No hay año escolar activo")
        return obj

    @classmethod
    def update_school_year(cls, pk, **kwargs):
        obj = cls.get_school_year(pk)
        if "start_date" in kwargs or "end_date" in kwargs:
            start = kwargs.get("start_date", obj.start_date)
            end = kwargs.get("end_date", obj.end_date)
            cls._validate_or_raise(start, end)
        allowed = {"start_date", "end_date", "is_active"}
        clean = {k: v for k, v in kwargs.items() if k in allowed}
        return cls.repository.update(pk, **clean)

    @classmethod
    def deactivate_school_year(cls, pk):
        obj = cls.get_school_year(pk)
        return cls.repository.update(pk, is_active=False)

    @classmethod
    def soft_delete(cls, pk, confirm=False):
        obj = cls.get_school_year(pk)
        counts = cls.repository.get_cascade_counts(pk)
        total = sum(counts.values())

        if total > 0 and not confirm:
            parts = [f"{v} {k}" for k, v in counts.items()]
            return {
                "requires_confirmation": True,
                "affected_records": total,
                "message": f"Esta acción desactivará {', '.join(parts)} relacionados",
                "id": obj.id,
                "is_active": True,
            }

        total = cls.repository.deactivate_cascade(pk)
        return {
            "id": obj.id,
            "is_active": False,
            "deactivated_records": total,
        }
