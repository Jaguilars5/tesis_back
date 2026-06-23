from django.db import models
from django.db.models import TextChoices
from apps.core.models import TimeStampedModel


class PromotionStatusChoices(TextChoices):
    APPROVED = "approved", "Aprobado"
    FAILED = "failed", "Reprobado"


class PeriodGradeSummary(TimeStampedModel):
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        related_name="grade_summaries",
        verbose_name="Matrícula",
    )
    subject_offering = models.ForeignKey(
        "academic.SubjectOffering",
        on_delete=models.CASCADE,
        related_name="grade_summaries",
        verbose_name="Oferta de Asignatura",
    )
    academic_period = models.ForeignKey(
        "academic.AcademicPeriod",
        on_delete=models.CASCADE,
        related_name="grade_summaries",
        verbose_name="Período Académico",
    )
    formative_avg = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Promedio Formativo"
    )
    summative_avg = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Promedio Sumativo"
    )
    final_avg_truncated = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Promedio Final Truncado"
    )
    qualitative_scale = models.ForeignKey(
        "grading.QualitativeScale",
        on_delete=models.PROTECT,
        null=True, blank=True,
        verbose_name="Escala Cualitativa",
    )
    is_failing = models.BooleanField(default=False, verbose_name="Está Reprobando")
    promotion_status = models.CharField(max_length=20, choices=PromotionStatusChoices.choices, null=True, blank=True, verbose_name="Estado de Promoción")
    calculated_at = models.DateTimeField(auto_now_add=True, verbose_name="Calculado en")
    calculated_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="grade_summaries_calculated", verbose_name="Calculado por",
    )
    approved_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="grade_summaries_approved", verbose_name="Aprobado por",
    )

    class Meta:
        app_label = "grading"
        verbose_name = "Resumen de Calificaciones del Período"
        verbose_name_plural = "Resúmenes de Calificaciones del Período"
        constraints = [
            models.UniqueConstraint(fields=["enrollment", "subject_offering", "academic_period"], name="unique_period_grade_summary"),
        ]
        indexes = [
            models.Index(fields=["academic_period", "subject_offering"]),
            models.Index(fields=["enrollment", "academic_period"]),
            models.Index(fields=["is_failing", "academic_period"]),
        ]

    def __str__(self):
        return f"{self.enrollment} - {self.subject_offering} ({self.academic_period})"
