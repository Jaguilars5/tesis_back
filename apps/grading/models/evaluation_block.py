from django.db import models
from apps.core.models import TimeStampedModel


class EvaluationBlock(TimeStampedModel):
    """
    BLOQUE_EVALUACION — Bloques formativo/sumativo/diagnóstico por período académico.
    Se configura al inicio de cada período.
    """

    code = models.CharField(max_length=50, blank=True, db_index=True, verbose_name="Código")
    academic_period = models.ForeignKey(
        "academic.AcademicPeriod",
        on_delete=models.CASCADE,
        related_name="evaluation_blocks",
        verbose_name="Período Académico",
    )
    subject_offering = models.ForeignKey(
        "academic.SubjectOffering",
        on_delete=models.CASCADE,
        related_name="evaluation_blocks",
        verbose_name="Oferta de Materia",
    )
    name = models.CharField(max_length=100, verbose_name="Nombre")
    evaluation_type = models.ForeignKey("grading.EvaluationType", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Tipo de evaluación")
    weight_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Porcentaje de Ponderación",
        help_text="Porcentaje que representa este bloque en la nota final del período",
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "grading"
        verbose_name = "Bloque de Evaluación"
        verbose_name_plural = "Bloques de Evaluación"
        ordering = ["academic_period", "subject_offering", "evaluation_type"]
        indexes = [
            models.Index(fields=["subject_offering", "academic_period"]),
        ]

    def __str__(self):
        return f"{self.academic_period.name} — {self.name} ({self.evaluation_type})"
