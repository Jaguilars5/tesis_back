from ..application import validators
from ..infrastructure.repositories import ActivityTypeRepository


class ActivityTypeService:
    """Lógica de negocio para tipos de actividad."""

    repository = ActivityTypeRepository

    @classmethod
    def create_activity_type(cls, code, name, description=""):
        errors = validators.run_all_validators(code=code, name=name, description=description)
        if errors:
            raise ValueError(errors)
        return cls.repository.create(
            code=code,
            name=name,
            description=description,
        )

    @classmethod
    def get_activity_type(cls, pk):
        obj = cls.repository.get_by_id(pk)
        if not obj:
            raise ValueError(f"Tipo de actividad {pk} no encontrado")
        return obj

    @classmethod
    def update_activity_type(cls, pk, **kwargs):
        cls.get_activity_type(pk)
        allowed = {"code", "name", "description", "is_active"}
        clean = {k: v for k, v in kwargs.items() if k in allowed}
        return cls.repository.update(pk, **clean)

    @classmethod
    def soft_delete(cls, pk, confirm=False):
        obj = cls.get_activity_type(pk)
        counts = cls.repository.get_cascade_counts(pk)
        total = sum(counts.values())

        if total > 0 and not confirm:
            parts = [f"{v} {k}" for k, v in counts.items()]
            return {
                "requires_confirmation": True,
                "affected_records": total,
                "message": f"Esta acci\u00f3n desactivar\u00e1 {', '.join(parts)} relacionados",
                "id": obj.id,
                "is_active": True,
            }

        total = cls.repository.deactivate_cascade(pk)
        return {
            "id": obj.id,
            "is_active": False,
            "deactivated_records": total,
        }
