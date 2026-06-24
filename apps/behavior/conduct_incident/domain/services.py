from ..infrastructure.repositories import ConductIncidentRepository


class ConductIncidentService:
    """Lógica de negocio para incidentes de conducta."""

    repository = ConductIncidentRepository

    @classmethod
    def create_conduct_incident(cls, **kwargs):
        return cls.repository.create(**kwargs)

    @classmethod
    def get_conduct_incident(cls, pk):
        obj = cls.repository.get_by_id(pk)
        if not obj:
            raise ValueError(f"Incidente de conducta {pk} no encontrado")
        return obj

    @classmethod
    def update_conduct_incident(cls, pk, **kwargs):
        obj = cls.get_conduct_incident(pk)
        for key, value in kwargs.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        obj.save()
        return obj

    @classmethod
    def delete_conduct_incident(cls, pk):
        obj = cls.get_conduct_incident(pk)
        obj.delete()
        return True
