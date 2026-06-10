from datetime import date
from django.db import models
from apps.core.models import TimeStampedModel
from apps.integration.models.syncable_mixin import SyncableModel


class BehaviorEvaluation(TimeStampedModel, SyncableModel):
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        related_name="attendance_behavior_evaluations",
        verbose_name="Matrícula",
    )
    academic_period = models.ForeignKey(
        "academic.AcademicPeriod",
        on_delete=models.CASCADE,
        related_name="attendance_behavior_evaluations",
        verbose_name="Período Académico",
    )
    calculated_scale = models.ForeignKey(
        "grading.QualitativeScale",
        on_delete=models.PROTECT,
        related_name="attendance_calculated_evaluations",
        verbose_name="Escala Calculada",
    )
    final_scale = models.ForeignKey(
        "grading.QualitativeScale",
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name="attendance_final_evaluations",
        verbose_name="Escala Final",
    )
    general_observation = models.TextField(null=True, blank=True, verbose_name="Observación general")
    override_reason = models.TextField(null=True, blank=True, verbose_name="Razón de anulación")
    created_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True,
        related_name="behavior_evaluations_created", verbose_name="Creado por",
    )
    evaluated_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True,
        related_name="behavior_evaluations", verbose_name="Evaluado por",
    )
    approved_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="behavior_evaluations_approved", verbose_name="Aprobado por",
    )
    evaluation_date = models.DateField(default=date.today, verbose_name="Fecha de evaluación")
    approval_date = models.DateField(null=True, blank=True, verbose_name="Fecha de aprobación")

    class Meta:
        app_label = "behavior"
        verbose_name = "Evaluación de Conducta"
        verbose_name_plural = "Evaluaciones de Conducta"
        unique_together = ("enrollment", "academic_period")
        indexes = [
            models.Index(fields=["academic_period", "calculated_scale"]),
            models.Index(fields=["evaluated_by", "evaluation_date"]),
        ]

    def __str__(self):
        return f"{self.enrollment} - {self.academic_period} ({self.calculated_scale})"
