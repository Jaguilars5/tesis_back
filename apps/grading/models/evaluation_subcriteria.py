from django.db import models


class EvaluationSubcriteria(models.Model):
    evaluation_criteria = models.ForeignKey(
        "grading.EvaluationCriteria",
        on_delete=models.CASCADE,
        related_name="subcriteria",
        verbose_name="Criterio de Evaluación",
    )
    name = models.CharField(max_length=100, verbose_name="Nombre")
    internal_weight = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Peso Interno (%)"
    )

    class Meta:
        app_label = "grading"
        verbose_name = "Subcriterio de Evaluación"
        verbose_name_plural = "Subcriterios de Evaluación"
        ordering = ["evaluation_criteria", "name"]

    def __str__(self):
        return f"{self.evaluation_criteria.name} - {self.name}"
