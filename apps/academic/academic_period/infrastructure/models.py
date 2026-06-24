from django.db import models
from apps.core.models import TimeStampedModel


def _get_default_period_type():
    from apps.academic.period_type.infrastructure.models import PeriodType

    from ..constants import DEFAULT_PERIOD_TYPE_CODE

    obj, _ = PeriodType.objects.get_or_create(
        code=DEFAULT_PERIOD_TYPE_CODE,
        defaults={"name": "Trimestre", "divisions_per_year": 3},
    )
    return obj.pk


class AcademicPeriod(TimeStampedModel):
    """Representa un período académico (ej: Quimestre 1, Parcial 1) dentro de un año escolar."""

    period_type = models.ForeignKey(
        "academic_period_type.PeriodType",
        on_delete=models.PROTECT,
        default=_get_default_period_type,
        verbose_name="Tipo de período",
    )
    school_year = models.ForeignKey(
        "institutions_school_year.SchoolYear",
        on_delete=models.CASCADE,
        related_name="academic_periods",
        verbose_name="Año Escolar",
    )
    code = models.CharField(
        max_length=50, blank=True, db_index=True, verbose_name="Código"
    )
    name = models.CharField(max_length=80, verbose_name="Nombre del Período")
    start_date = models.DateField(verbose_name="Fecha de Inicio")
    end_date = models.DateField(verbose_name="Fecha de Fin")
    year_weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Peso en el año (%)",
        help_text="Porcentaje de contribución de este período a la nota anual (ej: 40.00 para Q1)",
    )
    is_regular_period = models.BooleanField(
        default=True, verbose_name="Período Regular"
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "academic_period"
        verbose_name = "Período Académico"
        verbose_name_plural = "Períodos Académicos"

    def __str__(self):
        return self.name
