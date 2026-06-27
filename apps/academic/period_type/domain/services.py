from django.db import transaction

from ..application import validators
from ..infrastructure.repositories import PeriodTypeRepository


class PeriodTypeService:
    repository = PeriodTypeRepository

    @classmethod
    def _validate_or_raise(cls, **kwargs):
        errors = validators.run_all_validators(**kwargs)
        if errors:
            raise ValueError(errors)

    @classmethod
    @transaction.atomic
    def create_period_type(cls, code, name, description="", divisions_per_year=1):
        cls._validate_or_raise(
            code=code,
            name=name,
            divisions_per_year=divisions_per_year,
        )
        existing = cls.repository.first(code=code)
        if existing:
            raise ValueError({"code": "Ya existe un tipo de periodo con este codigo"})
        return cls.repository.create(
            code=code,
            name=name,
            description=description,
            divisions_per_year=divisions_per_year,
        )

    @classmethod
    def get_period_type(cls, period_type_id):
        obj = cls.repository.get_by_id(period_type_id)
        if not obj:
            raise ValueError({"id": f"Tipo de periodo {period_type_id} no encontrado"})
        return obj

    @classmethod
    @transaction.atomic
    def update_period_type(cls, period_type_id, **kwargs):
        allowed = {"code", "name", "description", "divisions_per_year", "is_active"}
        obj = cls.get_period_type(period_type_id)
        cls._validate_or_raise(
            code=kwargs.get("code", obj.code),
            name=kwargs.get("name", obj.name),
            divisions_per_year=kwargs.get("divisions_per_year", obj.divisions_per_year),
        )
        if "code" in kwargs:
            existing = cls.repository.first(code=kwargs["code"])
            if existing and existing.id != period_type_id:
                raise ValueError({"code": "Ya existe otro tipo de periodo con este codigo"})
        clean = {k: v for k, v in kwargs.items() if k in allowed}
        return cls.repository.update(obj.id, **clean)

    @classmethod
    @transaction.atomic
    def soft_delete(cls, pk, confirm=False):
        obj = cls.get_period_type(pk)
        counts = cls.repository.get_cascade_counts(pk)
        total = sum(counts.values())

        if total > 0 and not confirm:
            parts = [f"{v} {k}" for k, v in counts.items()]
            return {
                "requires_confirmation": True,
                "affected_records": total,
                "message": f"Esta accion desactivar\u00e1 {', '.join(parts)} relacionados",
                "id": obj.id,
                "is_active": True,
            }

        total = cls.repository.deactivate_cascade(pk)
        return {
            "id": obj.id,
            "is_active": False,
            "deactivated_records": total,
        }
