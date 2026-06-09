from django.db import models
from apps.core.models import TimeStampedModel


class RiskFactor(TimeStampedModel):
    code = models.CharField(max_length=30, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")

    class Meta:
        app_label = "analytics"
        verbose_name = "Factor de Riesgo"
        verbose_name_plural = "Factores de Riesgo"
        ordering = ["name"]

    def __str__(self):
        return self.name
