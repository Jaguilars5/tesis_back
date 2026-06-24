from django.db import models

from apps.core.models import TimeStampedModel


class SchoolYear(TimeStampedModel):
    """Representa un a\u00f1o escolar."""

    start_date = models.DateField(verbose_name="Fecha de Inicio")
    end_date = models.DateField(verbose_name="Fecha de Fin")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "institutions_school_year"
        verbose_name = "A\u00f1o Escolar"
        verbose_name_plural = "A\u00f1os Escolares"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.start_date} - {self.end_date}"

    @property
    def name(self):
        return str(self)
