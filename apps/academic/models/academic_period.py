from django.db import models
from apps.core.models import TimeStampedModel


def _get_default_period_type():
    from apps.academic.models import PeriodType
    obj, _ = PeriodType.objects.get_or_create(code="REGULAR", defaults={"name": "Regular"})
    return obj.pk


class AcademicPeriod(TimeStampedModel):
    code = models.CharField(max_length=50, blank=True, db_index=True, verbose_name="Código")
    school_year = models.ForeignKey(
        "institutions.SchoolYear",
        on_delete=models.CASCADE,
        verbose_name="Año Escolar",
    )
    parent_period = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="child_periods",
        verbose_name="Período Padre",
    )
    name = models.CharField(max_length=80, verbose_name="Nombre del Período")
    period_type = models.ForeignKey("academic.PeriodType", on_delete=models.PROTECT, default=_get_default_period_type, verbose_name="Tipo de período")
    start_date = models.DateField(verbose_name="Fecha de Inicio")
    end_date = models.DateField(verbose_name="Fecha de Fin")
    is_regular_period = models.BooleanField(
        default=True, verbose_name="Período Regular"
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "academic"
        verbose_name = "Período Académico"
        verbose_name_plural = "Períodos Académicos"

    def __str__(self):
        return self.name
