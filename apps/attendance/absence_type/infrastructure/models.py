from django.db import models

from apps.core.models import TimeStampedModel


class AbsenceType(TimeStampedModel):
    """Representa un tipo de ausencia (ej: justificada, injustificada)."""

    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        app_label = "attendance_absence_type"
        ordering = ["name"]

    def __str__(self):
        return self.name
