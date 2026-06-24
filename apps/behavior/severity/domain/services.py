from ..infrastructure.repositories import SeverityRepository


class SeverityService:
    """Lógica de negocio para severidades."""

    repository = SeverityRepository

    @classmethod
    def create_severity(cls, code, name, description=""):
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
        allowed = {"code", "name", "description", "is_active"}
        clean = {k: v for k, v in kwargs.items() if k in allowed}
        return cls.repository.update(pk, **clean)

    @classmethod
    def soft_delete_severity(cls, pk):
        obj = cls.get_severity(pk)
        return cls.repository.soft_delete(obj)
