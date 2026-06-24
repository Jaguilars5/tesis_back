from ..infrastructure.repositories import QualitativeScaleRepository


class QualitativeScaleService:
    """Lógica de negocio para escalas cualitativas."""

    repository = QualitativeScaleRepository

    @classmethod
    def create_qualitative_scale(cls, code, name, description, numeric_equivalence):
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
        allowed = {"code", "name", "description", "numeric_equivalence", "is_active"}
        clean = {k: v for k, v in kwargs.items() if k in allowed}
        return cls.repository.update(pk, **clean)
