from ..application import validators
from ..infrastructure.repositories import ConductIncidentRepository


class ConductIncidentService:
    """Lógica de negocio para incidentes de conducta."""

    repository = ConductIncidentRepository

    @classmethod
    def create_conduct_incident(cls, **kwargs):
        errors = validators.run_all_validators(**kwargs)
        if errors:
            raise ValueError(errors)
        return cls.repository.create(**kwargs)

    @classmethod
    def get_conduct_incident(cls, pk):
        obj = cls.repository.get_by_id(pk)
        if not obj:
            raise ValueError(f"Incidente de conducta {pk} no encontrado")
        return obj

    @classmethod
    def update_conduct_incident(cls, pk, **kwargs):
        cls.get_conduct_incident(pk)
        allowed = {
            "incident_type_id", "severity_id", "incident_date",
            "description", "actions_taken", "family_notified",
        }
        clean = {k: v for k, v in kwargs.items() if k in allowed}
        return cls.repository.update(pk, **clean)
