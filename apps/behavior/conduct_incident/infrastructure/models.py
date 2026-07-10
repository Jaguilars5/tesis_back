from django.db import models

from apps.core.models import TimeStampedModel
from apps.integration.infrastructure.models import SyncableModel


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
        verbose_name="Periodo Academico",
    )
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        related_name="conduct_incidents",
        verbose_name="Matricula",
    )

    incident_date = models.DateField(verbose_name="Fecha del Incidente")
    description = models.TextField(blank=True, default="", verbose_name="Descripcion")
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

    @property
    def enrollment_name(self):
        return str(self.enrollment) if self.enrollment else None

    @property
    def academic_period_name(self):
        return self.academic_period.name if self.academic_period else None

    @property
    def incident_type_name(self):
        return self.incident_type.name if self.incident_type else None

    @property
    def severity_name(self):
        return self.severity.name if self.severity else None

    def __str__(self):
        return f"{self.enrollment} - {self.incident_type} ({self.incident_date})"
