from ..application import validators
from ..infrastructure.repositories import SeverityRepository


class SeverityService:
    """Lógica de negocio para severidades."""

    repository = SeverityRepository

    @classmethod
    def create_severity(cls, code, name, description=""):
        errors = validators.run_all_validators(code=code, name=name, description=description)
        if errors:
            raise ValueError(errors)
        return cls.repository.create(
            code=code,
            name=name,
            description=description,
        )

    @classmethod
    def get_severity(cls, pk):
        obj = cls.repository.get_by_id(pk)
        if not obj:
            raise ValueError(f"Severidad {pk} no encontrada")
        return obj

    @classmethod
    def update_severity(cls, pk, **kwargs):
        cls.get_severity(pk)
        allowed = {"code", "name", "description", "is_active"}
        clean = {k: v for k, v in kwargs.items() if k in allowed}
        return cls.repository.update(pk, **clean)

    @classmethod
    def soft_delete_severity(cls, pk, confirm=False):
        obj = cls.get_severity(pk)
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
