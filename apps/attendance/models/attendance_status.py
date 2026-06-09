from django.db import models
from apps.core.models import TimeStampedModel


class AttendanceStatus(TimeStampedModel):
    code = models.CharField(max_length=10, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    tipo = models.CharField(
        max_length=10,
        choices=[("POSITIVO", "Positivo"), ("NEGATIVO", "Negativo")],
        null=True, blank=True, verbose_name="Tipo",
    )

    class Meta:
        app_label = "attendance"
        verbose_name = "Estado de Asistencia"
        verbose_name_plural = "Estados de Asistencia"
        ordering = ["name"]

    def __str__(self):
        return self.name
