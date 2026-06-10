from django.db import models
from apps.core.models import TimeStampedModel


class DayOfWeek(TimeStampedModel):
    code = models.IntegerField(unique=True, verbose_name="Código (1-7)")
    name = models.CharField(max_length=20, verbose_name="Nombre del día")

    class Meta:
        app_label = "academic"
        verbose_name = "Día de la Semana"
        verbose_name_plural = "Días de la Semana"
        ordering = ["code"]

    def __str__(self):
        return self.name
