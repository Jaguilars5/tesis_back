from django.db import models
from apps.core.models import TimeStampedModel


class EnrollmentStatus(TimeStampedModel):
    code = models.CharField(max_length=10, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "students"
        verbose_name = "Estado de Matrícula"
        verbose_name_plural = "Estados de Matrícula"
        ordering = ["name"]

    def __str__(self):
        return self.name
