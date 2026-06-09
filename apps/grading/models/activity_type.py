from django.db import models
from apps.core.models import TimeStampedModel


class ActivityType(TimeStampedModel):
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "grading"
        verbose_name = "Tipo de Actividad"
        verbose_name_plural = "Tipos de Actividad"
        ordering = ["name"]

    def __str__(self):
        return self.name
