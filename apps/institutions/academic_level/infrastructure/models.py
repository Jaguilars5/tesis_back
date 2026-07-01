from django.db import models

from apps.core.models import TimeStampedModel


class AcademicLevel(TimeStampedModel):
    name = models.CharField(max_length=100, verbose_name="Nombre del Nivel")
    code = models.CharField(max_length=50, db_index=True, verbose_name="Codigo")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "institutions_academic_level"
        verbose_name = "Nivel Academico"
        verbose_name_plural = "Niveles Academicos"
        ordering = ["name"]

    def __str__(self):
        return self.name
