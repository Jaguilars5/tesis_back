from django.db import models


class EvaluationBlock(models.Model):
    """
    BLOQUE_EVALUACION — Bloques formativo/sumativo/diagnóstico por período académico.
    Se configura al inicio de cada período.
    """

    TIPO_CHOICES = [
        ("DIAGNOSTICA", "Diagnóstica"),
        ("FORMATIVA", "Formativa"),
        ("SUMATIVA", "Sumativa"),
    ]

    academic_period = models.ForeignKey(
        "academic.Academic_Period",
        on_delete=models.CASCADE,
        related_name="evaluation_blocks",
        verbose_name="Período Académico",
    )
    name = models.CharField(max_length=100, verbose_name="Nombre")
    evaluation_type = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        verbose_name="Tipo de evaluación",
        help_text="DIAGNOSTICA, FORMATIVA o SUMATIVA",
    )
    weight_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Porcentaje de Ponderación",
        help_text="Porcentaje que representa este bloque en la nota final del período",
    )
    active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "grading"
        verbose_name = "Bloque de Evaluación"
        verbose_name_plural = "Bloques de Evaluación"
        ordering = ["academic_period", "evaluation_type"]

    def __str__(self):
        return f"{self.academic_period.name} — {self.name} ({self.evaluation_type})"
