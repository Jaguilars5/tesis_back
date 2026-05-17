from django.db import models


class EvaluationMacro(models.Model):
    academic_period = models.ForeignKey(
        "academic.Academic_Period",
        on_delete=models.CASCADE,
        related_name="evaluation_macros",
        verbose_name="Período Académico",
    )
    name = models.CharField(max_length=100, verbose_name="Nombre")
    weight_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Porcentaje de Peso"
    )
    active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "grading"
        verbose_name = "Macro Evaluación"
        verbose_name_plural = "Macro Evaluaciones"
        ordering = ["academic_period", "name"]

    def __str__(self):
        return f"{self.academic_period.name} - {self.name} ({self.weight_percentage}%)"
