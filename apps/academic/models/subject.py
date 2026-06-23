from django.db import models
from apps.core.models import TimeStampedModel


class Subject(TimeStampedModel):
    """Representa una materia o asignatura del plan de estudios."""

    name = models.CharField(max_length=255, verbose_name="Nombre de la Materia")
    code = models.CharField(max_length=100, unique=True, verbose_name="Código")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "academic"
        verbose_name = "Materia"
        verbose_name_plural = "Materias"

    def __str__(self):
        return self.name
