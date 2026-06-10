from django.db import models
from apps.core.models import TimeStampedModel
from apps.integration.models.syncable_mixin import SyncableModel


class RecoveryProcess(TimeStampedModel, SyncableModel):
    period_grade_summary = models.ForeignKey(
        "grading.PeriodGradeSummary",
        on_delete=models.CASCADE,
        related_name="recovery_processes",
        verbose_name="Resumen de Calificaciones",
    )
    subject_offering = models.ForeignKey(
        "academic.SubjectOffering",
        on_delete=models.CASCADE,
        verbose_name="Oferta de Materia",
    )
    managed_by_user = models.ForeignKey(
        "iam.User",
        on_delete=models.CASCADE,
        related_name="recovery_processes",
        verbose_name="Gestionado por",
    )
    process_type = models.ForeignKey("grading.RecoveryProcessType", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Tipo de proceso")
    initial_grade = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Nota Inicial")
    reinforcement_grade = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name="Nota de Refuerzo",
    )
    improvement_eval_grade = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name="Nota de Evaluación de Mejora",
    )
    final_calculated_grade = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name="Nota Final Calculada",
    )
    family_notified = models.BooleanField(default=False, verbose_name="Familia Notificada")
    family_notification_date = models.DateField(null=True, blank=True, verbose_name="Fecha de notificación familiar")
    start_date = models.DateField(verbose_name="Fecha de inicio")
    end_date = models.DateField(null=True, blank=True, verbose_name="Fecha de fin")
    reinforcement_plan = models.TextField(null=True, blank=True, verbose_name="Plan de refuerzo")
    objectives = models.TextField(null=True, blank=True, verbose_name="Objetivos")
    observations = models.TextField(null=True, blank=True, verbose_name="Observaciones")

    class Meta:
        app_label = "grading"
        verbose_name = "Proceso de Recuperación"
        verbose_name_plural = "Procesos de Recuperación"
        ordering = ["-start_date"]
        indexes = [
            models.Index(fields=["subject_offering", "start_date"]),
            models.Index(fields=["managed_by_user", "start_date"]),
        ]

    def __str__(self):
        return f"{self.period_grade_summary} - {self.process_type}"
