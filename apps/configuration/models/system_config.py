from django.db import models
from apps.core.models import TimeStampedModel


class SystemConfig(TimeStampedModel):
    key = models.CharField(max_length=255, primary_key=True, verbose_name="Clave")
    value = models.TextField(verbose_name="Valor")
    description = models.TextField(blank=True, verbose_name="Descripción")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")

    class Meta:
        app_label = "configuration"
        verbose_name = "Configuración del Sistema"
        verbose_name_plural = "Configuraciones del Sistema"

    def __str__(self):
        return self.key
