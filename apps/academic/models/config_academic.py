from django.db import models


class Config_Academic(models.Model):
    school_year = models.ForeignKey(
        "institutions.School_Year", on_delete=models.CASCADE, verbose_name="Año Escolar"
    )
    institution = models.ForeignKey(
        "institutions.Institution", on_delete=models.CASCADE, verbose_name="Institución"
    )
    name = models.CharField(max_length=80, verbose_name="Nombre")
    academic_period_type = models.CharField(
        max_length=20, verbose_name="Tipo de Período"
    )
    number_of_periods = models.IntegerField(verbose_name="Cantidad de Períodos")
    description = models.TextField(null=True, blank=True, verbose_name="Descripción")
    active = models.BooleanField(default=False, verbose_name="Activo")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de Actualización"
    )

    class Meta:
        app_label = "academic"
        verbose_name = "Configuración Académica"
        verbose_name_plural = "Configuraciones Académicas"

    def __str__(self):
        return f"{self.institution.name} - {self.name}"
