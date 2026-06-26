from django.db import models

from apps.core.models import TimeStampedModel


class AbsenceType(TimeStampedModel):
    """Representa un tipo de ausencia (ej: justificada, injustificada)."""

    code = models.CharField(max_length=30, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "attendance_absence_type"
        ordering = ["name"]
        verbose_name = "Tipo de Ausencia"
        verbose_name_plural = "Tipos de Ausencia"

    def __str__(self):
        return self.name
