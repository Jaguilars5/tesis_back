from django.db import models

from apps.core.models import TimeStampedModel


class AttendanceStatus(TimeStampedModel):
    """Representa un estado de asistencia (ej: Presente, Ausente, Tardanza)."""

    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        app_label = "attendance_attendance_status"
        verbose_name = "Estado de Asistencia"
        verbose_name_plural = "Estados de Asistencia"
        ordering = ["name"]

    def __str__(self):
        return self.name
