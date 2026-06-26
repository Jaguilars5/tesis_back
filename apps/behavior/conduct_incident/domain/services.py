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

    @classmethod
    def delete_conduct_incident(cls, pk):
        cls.get_conduct_incident(pk)
        cls.repository.delete(pk)
        return True

    @classmethod
    def soft_delete(cls, pk, confirm=False):
        obj = cls.get_conduct_incident(pk)
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
