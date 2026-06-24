from django.core.validators import MinValueValidator
from django.db import models

from apps.core.models import TimeStampedModel


class PeriodType(TimeStampedModel):
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    divisions_per_year = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Divisiones por año",
        help_text="Cantidad de veces que el año escolar se divide con este tipo de período (ej: 3 para Trimestre, 2 para Semestre, 4 para Bimestre).",
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "academic_period_type"
        verbose_name = "Tipo de Período"
        verbose_name_plural = "Tipos de Período"
        ordering = ["name"]

    def __str__(self):
        return self.name
