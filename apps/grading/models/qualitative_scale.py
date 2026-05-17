from django.db import models


class QualitativeScale(models.Model):
    code = models.CharField(max_length=10, unique=True, verbose_name="Código")
    description = models.CharField(max_length=100, verbose_name="Descripción")
    numeric_equivalence = models.DecimalField(
        max_digits=4, decimal_places=2, verbose_name="Equivalencia Numérica"
    )

    class Meta:
        app_label = "grading"
        verbose_name = "Escala Cualitativa"
        verbose_name_plural = "Escalas Cualitativas"
        ordering = ["-numeric_equivalence"]

    def __str__(self):
        return self.description
