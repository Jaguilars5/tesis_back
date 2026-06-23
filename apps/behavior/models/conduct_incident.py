from django.db import models
from apps.core.models import TimeStampedModel
from apps.integration.models.syncable_mixin import SyncableModel


class ConductIncident(TimeStampedModel, SyncableModel):
    incident_type = models.ForeignKey(
        "behavior.IncidentType",
        on_delete=models.PROTECT,
        verbose_name="Tipo de incidente",
    )
    severity = models.ForeignKey(
        "behavior.Severity",
        on_delete=models.PROTECT,
        verbose_name="Severidad",
    )
    academic_period = models.ForeignKey(
        "academic.AcademicPeriod",
        on_delete=models.CASCADE,
        related_name="conduct_incidents",
        verbose_name="Período Académico",
    )
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        related_name="conduct_incidents",
        verbose_name="Matrícula",
    )

    incident_date = models.DateField(verbose_name="Fecha del Incidente")

    description = models.TextField(blank=True, default="", verbose_name="Descripción")
    actions_taken = models.TextField(
        blank=True, default="", verbose_name="Acciones tomadas"
    )
    family_notified = models.BooleanField(
        default=False, verbose_name="Familia Notificada"
    )

    class Meta:
        app_label = "behavior"
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
