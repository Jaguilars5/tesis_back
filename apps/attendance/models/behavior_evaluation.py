from django.db import models


class BehaviorEvaluation(models.Model):
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        related_name="attendance_behavior_evaluations",
        verbose_name="Matrícula",
    )
    academic_period = models.ForeignKey(
        "academic.Academic_Period",
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

    class Meta:
        app_label = "attendance"
        verbose_name = "Evaluación de Conducta"
        verbose_name_plural = "Evaluaciones de Conducta"
        unique_together = ("enrollment", "academic_period")

    def __str__(self):
        return f"{self.enrollment} - {self.academic_period} ({self.calculated_scale})"
