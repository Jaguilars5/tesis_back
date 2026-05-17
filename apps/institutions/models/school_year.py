from django.db import models


class School_Year(models.Model):
    institution = models.ForeignKey(
        "institutions.Institution", on_delete=models.CASCADE, verbose_name="Institución"
    )
    academic_regime = models.ForeignKey(
        "institutions.AcademicRegime",
        on_delete=models.CASCADE,
        verbose_name="Régimen Académico",
        null=True,
    )
    name = models.CharField(max_length=255, verbose_name="Nombre del Año Escolar")
    start_date = models.DateField(verbose_name="Fecha de Inicio")
    end_date = models.DateField(verbose_name="Fecha de Fin")
    active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de Actualización"
    )

    class Meta:
        app_label = "institutions"
        verbose_name = "Año Escolar"
        verbose_name_plural = "Años Escolares"

    def __str__(self):
        return f"{self.institution.name} - {self.start_date} - {self.end_date}"
