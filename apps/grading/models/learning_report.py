from django.db import models
from apps.core.models import TimeStampedModel
from apps.integration.models.syncable_mixin import SyncableModel


class LearningReport(TimeStampedModel, SyncableModel):
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        verbose_name="Matrícula",
    )
    academic_period = models.ForeignKey(
        "academic.AcademicPeriod",
        on_delete=models.CASCADE,
        verbose_name="Período Académico",
    )
    formative_avg = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name="Promedio Formativo",
    )
    summative_avg = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name="Promedio Sumativo",
    )
    final_avg = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name="Promedio Final",
    )
    attendance_rate = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name="Tasa de Asistencia",
    )
    behavior_scale = models.ForeignKey(
        "grading.QualitativeScale",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Escala de Conducta",
    )
    general_observations = models.TextField(null=True, blank=True, verbose_name="Observaciones generales")
    recommendations = models.TextField(null=True, blank=True, verbose_name="Recomendaciones")
    created_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True,
        related_name="created_reports", verbose_name="Creado por",
    )
    evaluated_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True,
        related_name="evaluated_reports", verbose_name="Evaluado por",
    )
    approved_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="approved_reports", verbose_name="Aprobado por",
    )
    is_final = models.BooleanField(default=False, verbose_name="Es definitivo")

    class Meta:
        app_label = "grading"
        verbose_name = "Informe de Aprendizaje"
        verbose_name_plural = "Informes de Aprendizaje"
        unique_together = [("enrollment", "academic_period")]
        ordering = ["-academic_period__start_date"]
        indexes = [
            models.Index(fields=["academic_period", "is_final"]),
        ]

    def __str__(self):
        return f"{self.enrollment} - {self.academic_period}"
