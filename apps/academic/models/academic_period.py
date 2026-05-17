from django.db import models


class Academic_Period(models.Model):
    school_year = models.ForeignKey(
        "institutions.School_Year",
        on_delete=models.CASCADE,
        verbose_name="Año Escolar",
        null=True,
    )
    name = models.CharField(max_length=80, verbose_name="Nombre del Período")
    start_date = models.DateField(verbose_name="Fecha de Inicio")
    end_date = models.DateField(verbose_name="Fecha de Fin")
    is_regular_period = models.BooleanField(default=True, verbose_name="Período Regular")
    active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")

    class Meta:
        app_label = "academic"
        verbose_name = "Período Académico"
        verbose_name_plural = "Períodos Académicos"

    def __str__(self):
        return self.name
