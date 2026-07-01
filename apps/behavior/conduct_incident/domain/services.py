import logging

from django.db import transaction

from ..application import validators
from ..infrastructure.repositories import ConductIncidentRepository

logger = logging.getLogger(__name__)


class ConductIncidentService:
    """Lógica de negocio para incidentes de conducta."""

    repository = ConductIncidentRepository

    @classmethod
    def create_conduct_incident(cls, **kwargs):
        errors = validators.run_all_validators(**kwargs)
        if errors:
            raise ValueError(errors)
        incident = cls.repository.create(**kwargs)
        cls._enqueue_post_create(incident)
        return incident

    @classmethod
    def _enqueue_post_create(cls, incident):
        """Programa, al confirmar la transacción, la notificación al estudiante/
        representantes y el recálculo del promedio de conducta del periodo.
        """
        try:
            from apps.core.notifications.tasks import notify_incident_created
            from ..tasks import recalculate_conduct_average_task

            incident_id = incident.id
            enrollment_id = incident.enrollment_id
            academic_period_id = incident.academic_period_id

            transaction.on_commit(
                lambda: notify_incident_created.delay(incident_id)
            )
            transaction.on_commit(
                lambda: recalculate_conduct_average_task.delay(
                    enrollment_id, academic_period_id
                )
            )
        except Exception:
            logger.warning(
                "No se pudo programar el post-create del incidente incident=%s",
                getattr(incident, "id", None),
                exc_info=True,
            )

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
