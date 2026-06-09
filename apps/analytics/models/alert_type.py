from django.db import models
from apps.core.models import TimeStampedModel


class AlertType(TimeStampedModel):
    code = models.CharField(max_length=50, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "analytics"
        verbose_name = "Tipo de Alerta"
        verbose_name_plural = "Tipos de Alerta"
        ordering = ["name"]

    def __str__(self):
        return self.name
