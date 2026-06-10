from django.db import models
from apps.core.models import TimeStampedModel
from apps.integration.models.syncable_mixin import SyncableModel


class DiagnosticEvaluation(TimeStampedModel, SyncableModel):
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        related_name="diagnostic_evaluations",
        verbose_name="Matrícula",
    )
    academic_period = models.ForeignKey(
        "academic.AcademicPeriod",
        on_delete=models.CASCADE,
        related_name="diagnostic_evaluations",
        verbose_name="Período Académico",
    )
    applied_by_user = models.ForeignKey(
        "iam.User",
        on_delete=models.CASCADE,
        related_name="diagnostic_evaluations",
        verbose_name="Aplicada por",
    )
    socioemotional_area = models.ForeignKey(
        "behavior.SocioemotionalArea",
        on_delete=models.PROTECT,
        verbose_name="Área Socioemocional",
    )
    findings_description = models.TextField(verbose_name="Descripción de hallazgos")
    development_level = models.ForeignKey(
        "behavior.DevelopmentLevel",
        on_delete=models.PROTECT,
        verbose_name="Nivel de Desarrollo",
    )
    application_date = models.DateField(verbose_name="Fecha de aplicación")
    recommendations = models.TextField(null=True, blank=True, verbose_name="Recomendaciones")

    class Meta:
        app_label = "behavior"
        verbose_name = "Evaluación Diagnóstica"
        verbose_name_plural = "Evaluaciones Diagnósticas"
        ordering = ["-application_date"]

    def __str__(self):
        return f"{self.enrollment} - {self.socioemotional_area} ({self.application_date})"
