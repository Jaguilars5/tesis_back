from ..infrastructure.repositories import ActivityTypeRepository


class ActivityTypeService:
    """Lógica de negocio para tipos de actividad."""

    repository = ActivityTypeRepository

    @classmethod
    def create_activity_type(cls, code, name, description=""):
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
        allowed = {"code", "name", "description", "is_active"}
        clean = {k: v for k, v in kwargs.items() if k in allowed}
        return cls.repository.update(pk, **clean)
