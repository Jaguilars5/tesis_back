from django.db import models


class Subject(models.Model):
    school_year = models.ForeignKey(
        "institutions.School_Year", on_delete=models.CASCADE, verbose_name="Año Escolar"
    )
    section = models.ForeignKey(
        "academic.Section", on_delete=models.CASCADE, verbose_name="Sección"
    )
    name = models.CharField(max_length=255, verbose_name="Nombre de la Materia")
    code = models.CharField(max_length=100, unique=True, verbose_name="Código")
    weekly_hours = models.IntegerField(verbose_name="Horas Semanales")
    approve_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Porcentaje de Aprobación"
    )
    active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de Actualización"
    )

    class Meta:
        app_label = "academic"
        verbose_name = "Materia"
        verbose_name_plural = "Materias"

    def __str__(self):
        return f"{self.school_year.institution.name} - {self.section} - {self.name}"
