import datetime
import uuid
from django.db import models
from apps.core.models import TimeStampedModel
from apps.integration.models.syncable_mixin import SyncableModel


class BehaviorEvaluation(TimeStampedModel, SyncableModel):
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        related_name="behavior_evaluations",
        verbose_name="Matrícula",
    )
    academic_period = models.ForeignKey(
        "academic.AcademicPeriod",
        on_delete=models.CASCADE,
        related_name="behavior_evaluations",
        verbose_name="Período Académico",
    )
    evaluated_by = models.ForeignKey(
        "iam.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="behavior_evaluations",
        verbose_name="Evaluado por",
    )
    approved_by = models.ForeignKey(
        "iam.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="behavior_evaluations_approved",
        verbose_name="Aprobado por",
    )
    created_by = models.ForeignKey(
        "iam.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="behavior_evaluations_created",
        verbose_name="Creado por",
    )
    calculated_scale = models.ForeignKey(
        "grading.QualitativeScale",
        on_delete=models.PROTECT,
        related_name="calculated_evaluations",
        verbose_name="Escala Calculada",
    )
    final_scale = models.ForeignKey(
        "grading.QualitativeScale",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="final_evaluations",
        verbose_name="Escala Final",
    )
    general_observation = models.TextField(
        blank=True, default="", verbose_name="Observación general"
    )
    override_reason = models.TextField(
        blank=True, default="", verbose_name="Razón de anulación"
    )
    evaluation_date = models.DateField(
        default=datetime.date.today, verbose_name="Fecha de evaluación"
    )
    approval_date = models.DateField(
        null=True, blank=True, verbose_name="Fecha de aprobación"
    )

    class Meta:
        app_label = "behavior"
        verbose_name = "Evaluación de Conducta"
        verbose_name_plural = "Evaluaciones de Conducta"
        unique_together = [("enrollment", "academic_period")]
        indexes = [
            models.Index(fields=["academic_period", "calculated_scale"]),
            models.Index(fields=["evaluated_by", "evaluation_date"]),
        ]

    def __str__(self):
        scale = self.final_scale or self.calculated_scale
        scale_code = scale.code if scale else "Sin escala"
        return f"{self.enrollment} - {self.academic_period} - {scale_code}"
