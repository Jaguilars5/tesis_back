from django.db import models


class EvaluationCriteria(models.Model):
    evaluation_macro = models.ForeignKey(
        "grading.EvaluationMacro",
        on_delete=models.CASCADE,
        related_name="criteria",
        verbose_name="Macro Evaluación",
    )
    name = models.CharField(max_length=100, verbose_name="Nombre")
    internal_weight = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Peso Interno (%)"
    )

    class Meta:
        app_label = "grading"
        verbose_name = "Criterio de Evaluación"
        verbose_name_plural = "Criterios de Evaluación"
        ordering = ["evaluation_macro", "name"]

    def __str__(self):
        return f"{self.evaluation_macro.name} - {self.name}"
