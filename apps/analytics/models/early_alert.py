from django.db import models
from django.db.models import TextChoices
from apps.core.models import TimeStampedModel
from apps.integration.models.syncable_mixin import SyncableModel


class AlertTypeChoices(TextChoices):
    LOW_ATTENDANCE = "low_attendance", "Baja Asistencia"
    FAILING_GRADES = "failing_grades", "Calificaciones Bajas"
    BEHAVIORAL = "behavioral", "Problemas de Conducta"
    DROPOUT_RISK = "dropout_risk", "Riesgo de Deserción"
    SOCIOEMOTIONAL = "socioemotional", "Problemas Socioemocionales"


class UrgencyLevelChoices(TextChoices):
    LOW = "low", "Baja"
    MEDIUM = "medium", "Media"
    HIGH = "high", "Alta"
    CRITICAL = "critical", "Crítica"


class EarlyAlert(TimeStampedModel, SyncableModel):
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        related_name="early_alerts",
        verbose_name="Matrícula",
    )
    academic_period = models.ForeignKey(
        "academic_period.AcademicPeriod",
        on_delete=models.CASCADE,
        related_name="early_alerts",
        verbose_name="Período Académico",
    )
    alert_type = models.CharField(max_length=30, choices=AlertTypeChoices.choices, null=True, blank=True, verbose_name="Tipo de alerta")
    description = models.TextField(verbose_name="Descripción")
    urgency_level = models.CharField(max_length=20, choices=UrgencyLevelChoices.choices, null=True, blank=True, verbose_name="Nivel de urgencia")
    attended = models.BooleanField(default=False, verbose_name="Atendida")
    attended_by_user = models.ForeignKey(
        "iam.User",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="attended_alerts",
        verbose_name="Atendida por",
    )
    detected_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de detección")
    attended_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de atención")
    response_actions = models.TextField(blank=True, default='', verbose_name="Acciones de respuesta")

    class Meta:
        app_label = "analytics"
        verbose_name = "Alerta Temprana"
        verbose_name_plural = "Alertas Tempranas"
        ordering = ["-detected_at"]
        indexes = [
            models.Index(fields=["attended", "urgency_level"]),
            models.Index(fields=["enrollment", "academic_period"]),
        ]

    def __str__(self):
        return f"{self.get_alert_type_display() if self.alert_type else ''} - {self.enrollment} ({self.get_urgency_level_display() if self.urgency_level else ''})"
