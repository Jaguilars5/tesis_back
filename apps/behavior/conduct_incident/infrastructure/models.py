from django.db import models

from apps.core.models import TimeStampedModel
from apps.integration.models.syncable_mixin import SyncableModel


class ConductIncident(TimeStampedModel, SyncableModel):
    """Representa un incidente de conducta de un estudiante."""

    incident_type = models.ForeignKey(
        "behavior_incident_type.IncidentType",
        on_delete=models.PROTECT,
        verbose_name="Tipo de incidente",
    )
    severity = models.ForeignKey(
        "behavior_severity.Severity",
        on_delete=models.PROTECT,
        verbose_name="Severidad",
    )
    academic_period = models.ForeignKey(
        "academic_period.AcademicPeriod",
        on_delete=models.CASCADE,
        related_name="conduct_incidents",
        verbose_name="Per\u00edodo Academico",
    )
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        related_name="conduct_incidents",
        verbose_name="Matr\u00edcula",
    )

    incident_date = models.DateField(verbose_name="Fecha del Incidente")
    description = models.TextField(blank=True, default="", verbose_name="Descripci\u00f3n")
    actions_taken = models.TextField(blank=True, default="", verbose_name="Acciones tomadas")
    family_notified = models.BooleanField(default=False, verbose_name="Familia Notificada")

    class Meta:
        app_label = "behavior_conduct_incident"
        verbose_name = "Incidente de Conducta"
        verbose_name_plural = "Incidentes de Conducta"
        ordering = ["-incident_date"]
        indexes = [
            models.Index(fields=["enrollment", "academic_period"]),
            models.Index(fields=["academic_period", "severity"]),
            models.Index(fields=["incident_date"]),
        ]

    def __str__(self):
        return f"{self.enrollment} - {self.incident_type} ({self.incident_date})"
