from ..infrastructure.repositories import IncidentTypeRepository


class IncidentTypeService:
    """Lógica de negocio para tipos de incidente."""

    repository = IncidentTypeRepository

    @classmethod
    def create_incident_type(cls, code, name, description=""):
        return cls.repository.create(
            code=code,
            name=name,
            description=description,
        )

    @classmethod
    def get_incident_type(cls, pk):
        obj = cls.repository.get_by_id(pk)
        if not obj:
            raise ValueError(f"Tipo de incidente {pk} no encontrado")
        return obj

    @classmethod
    def update_incident_type(cls, pk, **kwargs):
        allowed = {"code", "name", "description", "is_active"}
        clean = {k: v for k, v in kwargs.items() if k in allowed}
        return cls.repository.update(pk, **clean)

    @classmethod
    def soft_delete_incident_type(cls, pk):
        obj = cls.get_incident_type(pk)
        return cls.repository.soft_delete(obj)
