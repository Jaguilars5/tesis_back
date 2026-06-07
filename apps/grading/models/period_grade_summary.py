from django.db import models


class PeriodGradeSummary(models.Model):
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
        "academic.Academic_Period",
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
    requires_recovery = models.BooleanField(default=False, verbose_name="Requiere Recuperación")
    promotion_status = models.CharField(
        max_length=20,
        null=True, blank=True,
        choices=[
            ("approved", "Aprobado"),
            ("failed", "Reprobado"),
            ("recovery", "En Recuperación"),
        ],
        verbose_name="Estado de Promoción",
    )
    calculated_at = models.DateTimeField(auto_now_add=True, verbose_name="Calculado en")

    class Meta:
        app_label = "grading"
        verbose_name = "Resumen de Calificaciones del Período"
        verbose_name_plural = "Resúmenes de Calificaciones del Período"
        unique_together = ("enrollment", "subject_offering", "academic_period")

    def __str__(self):
        return f"{self.enrollment} - {self.subject_offering} ({self.academic_period})"
