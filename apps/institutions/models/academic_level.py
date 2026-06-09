from django.db import models
from apps.core.models import TimeStampedModel


class AcademicLevel(TimeStampedModel):
    code = models.CharField(max_length=50, blank=True, db_index=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre del Nivel")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "institutions"
        verbose_name = "Nivel Académico"
        verbose_name_plural = "Niveles Académicos"
        ordering = ["name"]

    def __str__(self):
        return self.name
