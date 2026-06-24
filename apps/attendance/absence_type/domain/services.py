from ..infrastructure.repositories import AbsenceTypeRepository


class AbsenceTypeService:
    """Lógica de negocio para tipos de ausencia."""

    repository = AbsenceTypeRepository

    @classmethod
    def create_absence_type(cls, code, name, description=""):
        return cls.repository.create(
            code=code,
            name=name,
            description=description,
        )

    @classmethod
    def get_absence_type(cls, pk):
        obj = cls.repository.get_by_id(pk)
        if not obj:
            raise ValueError(f"Tipo de ausencia {pk} no encontrado")
        return obj

    @classmethod
    def update_absence_type(cls, pk, **kwargs):
        allowed = {"code", "name", "description", "is_active"}
        clean = {k: v for k, v in kwargs.items() if k in allowed}
        return cls.repository.update(pk, **clean)
