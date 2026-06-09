from django.db import models
from apps.core.models import TimeStampedModel


class SocioemotionalSkill(TimeStampedModel):
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(null=True, blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activa")

    class Meta:
        app_label = "behavior"
        verbose_name = "Habilidad Socioemocional"
        verbose_name_plural = "Habilidades Socioemocionales"
        ordering = ["name"]

    def __str__(self):
        return self.name
