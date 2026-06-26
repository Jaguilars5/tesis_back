from ..application import validators
from ..infrastructure.repositories import QualitativeScaleRepository


class QualitativeScaleService:
    """Lógica de negocio para escalas cualitativas."""

    repository = QualitativeScaleRepository

    @classmethod
    def create_qualitative_scale(cls, code, name, description, numeric_equivalence):
        errors = validators.run_all_validators(
            code=code, name=name, description=description,
            numeric_equivalence=numeric_equivalence,
        )
        if errors:
            raise ValueError(errors)
        return cls.repository.create(
            code=code,
            name=name,
            description=description,
            numeric_equivalence=numeric_equivalence,
        )

    @classmethod
    def get_qualitative_scale(cls, pk):
        obj = cls.repository.get_by_id(pk)
        if not obj:
            raise ValueError(f"Escala cualitativa {pk} no encontrada")
        return obj

    @classmethod
    def get_by_code(cls, code):
        return cls.repository.get_by_code(code)

    @classmethod
    def update_qualitative_scale(cls, pk, **kwargs):
        cls.get_qualitative_scale(pk)
        allowed = {"code", "name", "description", "numeric_equivalence", "is_active"}
        clean = {k: v for k, v in kwargs.items() if k in allowed}
        return cls.repository.update(pk, **clean)

    @classmethod
    def soft_delete(cls, pk, confirm=False):
        obj = cls.get_qualitative_scale(pk)
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
