import datetime

from django.db import models

from apps.core.models import TimeStampedModel
from apps.integration.infrastructure.models import SyncableModel


class BehaviorEvaluation(TimeStampedModel, SyncableModel):
    """Representa una evaluación de conducta de un estudiante en un período."""

    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        related_name="behavior_evaluations",
        verbose_name="Matricula",
    )
    academic_period = models.ForeignKey(
        "academic_period.AcademicPeriod",
        on_delete=models.CASCADE,
        related_name="behavior_evaluations",
        verbose_name="Periodo Academico",
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
        "grading_qualitative_scale.QualitativeScale",
        on_delete=models.PROTECT,
        related_name="calculated_evaluations",
        verbose_name="Escala Calculada",
    )
    final_scale = models.ForeignKey(
        "grading_qualitative_scale.QualitativeScale",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="final_evaluations",
        verbose_name="Escala Final",
    )
    general_observation = models.TextField(
        blank=True, default="", verbose_name="Observacion general"
    )
    override_reason = models.TextField(
        blank=True, default="", verbose_name="Razon de anulacion"
    )
    evaluation_date = models.DateField(
        default=datetime.date.today, verbose_name="Fecha de evaluacion"
    )
    approval_date = models.DateField(
        null=True, blank=True, verbose_name="Fecha de aprobacion"
    )

    class Meta:
        app_label = "behavior_evaluation"
        verbose_name = "Evaluacion de Conducta"
        verbose_name_plural = "Evaluaciones de Conducta"
        unique_together = [("enrollment", "academic_period")]
        indexes = [
            models.Index(fields=["academic_period", "calculated_scale"]),
            models.Index(fields=["evaluated_by", "evaluation_date"]),
        ]

    @property
    def enrollment_name(self):
        return str(self.enrollment) if self.enrollment else None

    @property
    def academic_period_name(self):
        return self.academic_period.name if self.academic_period else None

    @property
    def calculated_scale_name(self):
        return self.calculated_scale.name if self.calculated_scale else None

    @property
    def final_scale_name(self):
        return self.final_scale.name if self.final_scale else None

    def __str__(self):
        scale = self.final_scale or self.calculated_scale
        scale_code = scale.code if scale else "Sin escala"
        return f"{self.enrollment} - {self.academic_period} - {scale_code}"
