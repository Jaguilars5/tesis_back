from django.db import models


class Academic_Period(models.Model):
    school_year = models.ForeignKey(
        "institutions.School_Year",
        on_delete=models.CASCADE,
        verbose_name="Año Escolar",
    )
    name = models.CharField(max_length=80, verbose_name="Nombre del Período")
    # Normalizar los tipos de período a un modelo aparte
    period_type = models.CharField(
        max_length=20,
        choices=[
            ("REGULAR", "Regular"),
            ("SUPLETORIO", "Supletorio"),
            ("REFUERZO", "Refuerzo"),
        ],
        default="REGULAR",
        verbose_name="Tipo de período",
    )
    start_date = models.DateField(verbose_name="Fecha de Inicio")
    end_date = models.DateField(verbose_name="Fecha de Fin")
    is_regular_period = models.BooleanField(
        default=True, verbose_name="Período Regular"
    )

    class Meta:
        app_label = "academic"
        verbose_name = "Período Académico"
        verbose_name_plural = "Períodos Académicos"

    def __str__(self):
        return self.name
