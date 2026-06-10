from django.db import models
from apps.core.models import TimeStampedModel


class RecoveryProcessHistory(TimeStampedModel):
    recovery_process = models.ForeignKey(
        "grading.RecoveryProcess",
        on_delete=models.CASCADE,
        verbose_name="Proceso de Recuperación",
    )
    action = models.CharField(max_length=30, choices=[
        ("STARTED", "Iniciado"),
        ("GRADE_UPDATED", "Calificación actualizada"),
        ("SESSION_COMPLETED", "Sesión completada"),
        ("COMPLETED", "Completado"),
        ("CANCELLED", "Cancelado"),
    ], verbose_name="Acción")
    previous_grade = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name="Calificación Anterior",
    )
    new_grade = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name="Nueva Calificación",
    )
    previous_status = models.ForeignKey(
        "grading.RecoveryProcessStatus",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="previous_recovery",
        verbose_name="Estado Anterior",
    )
    new_status = models.ForeignKey(
        "grading.RecoveryProcessStatus",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="new_recovery",
        verbose_name="Nuevo Estado",
    )
    notes = models.TextField(blank=True, verbose_name="Notas")
    changed_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True,
        verbose_name="Cambiado por",
    )

    class Meta:
        app_label = "grading"
        verbose_name = "Historial de Proceso de Recuperación"
        verbose_name_plural = "Historiales de Procesos de Recuperación"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.recovery_process} - {self.action}"
