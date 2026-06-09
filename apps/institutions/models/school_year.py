from django.db import models
from apps.core.models import TimeStampedModel


class SchoolYear(TimeStampedModel):
    name = models.CharField(max_length=255, verbose_name="Nombre del Año Escolar")
    start_date = models.DateField(verbose_name="Fecha de Inicio")
    end_date = models.DateField(verbose_name="Fecha de Fin")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    class Meta:
        app_label = "institutions"
        verbose_name = "Año Escolar"
        verbose_name_plural = "Años Escolares"

    def __str__(self):
        return f"{self.name} - {self.start_date} - {self.end_date}"
