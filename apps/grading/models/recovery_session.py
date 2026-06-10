from django.db import models
from apps.core.models import TimeStampedModel
from apps.integration.models.syncable_mixin import SyncableModel


class RecoverySession(TimeStampedModel, SyncableModel):
    recovery_process = models.ForeignKey(
        "grading.RecoveryProcess",
        on_delete=models.CASCADE,
        related_name="sessions",
        verbose_name="Proceso de Recuperación",
    )
    session_date = models.DateField(verbose_name="Fecha de la sesión")
    duration_minutes = models.IntegerField(default=60, verbose_name="Duración (minutos)")
    topics_covered = models.TextField(blank=True, verbose_name="Temas cubiertos")
    student_present = models.BooleanField(default=True, verbose_name="Estudiante presente")
    teacher_observation = models.TextField(null=True, blank=True, verbose_name="Observación del docente")

    class Meta:
        app_label = "grading"
        verbose_name = "Sesión de Refuerzo"
        verbose_name_plural = "Sesiones de Refuerzo"
        ordering = ["session_date"]

    def __str__(self):
        return f"Sesión {self.session_date} - {self.recovery_process}"
