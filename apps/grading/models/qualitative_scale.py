from django.db import models
from apps.core.models import TimeStampedModel


class QualitativeScale(TimeStampedModel):
    code = models.CharField(max_length=10, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, blank=True, verbose_name="Nombre")
    description = models.TextField(verbose_name="Descripción")
    numeric_equivalence = models.DecimalField(max_digits=4, decimal_places=2, verbose_name="Equivalencia Numérica")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    applicable_sublevel = models.CharField(max_length=50, null=True, blank=True, verbose_name="Subnivel Aplicable")

    class Meta:
        app_label = "grading"
        verbose_name = "Escala Cualitativa"
        verbose_name_plural = "Escalas Cualitativas"
        ordering = ["-numeric_equivalence"]

    def __str__(self):
        return f"{self.code} — {self.description}"
