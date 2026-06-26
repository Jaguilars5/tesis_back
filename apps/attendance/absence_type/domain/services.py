from django.db import transaction

from ..application import validators
from ..infrastructure.repositories import AbsenceTypeRepository


class AbsenceTypeService:
    """Lógica de negocio para tipos de ausencia."""

    repository = AbsenceTypeRepository

    @classmethod
    def get_absence_type(cls, pk):
        obj = cls.repository.get_by_id(pk)
        if not obj:
            raise ValueError(f"Tipo de ausencia {pk} no encontrado")
        return obj

    @classmethod
    @transaction.atomic
    def create_absence_type(cls, code, name, description=""):
        errors = validators.run_all_validators(code=code, name=name)
        if errors:
            raise ValueError(errors)
        return cls.repository.create(
            code=code,
            name=name,
            description=description,
        )

    @classmethod
    @transaction.atomic
    def update_absence_type(cls, pk, **kwargs):
        cls.get_absence_type(pk)
        allowed = {"code", "name", "description", "is_active"}
        clean = {k: v for k, v in kwargs.items() if k in allowed}
        errors = validators.run_all_validators(
            code=clean.get("code"),
            name=clean.get("name"),
            exclude_id=pk,
            partial=True,
        )
        if errors:
            raise ValueError(errors)
        return cls.repository.update(pk, **clean)

    @classmethod
    @transaction.atomic
    def soft_delete(cls, pk, confirm=False):
        obj = cls.get_absence_type(pk)
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
