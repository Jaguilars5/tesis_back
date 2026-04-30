from django.db import models


class Section(models.Model):
    school_year = models.ForeignKey(
        "institutions.School_Year", on_delete=models.CASCADE, verbose_name="Año Escolar"
    )
    timing_regime = models.ForeignKey(
        "academic.Timing_Regime",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Régimen de Horario",
    )
    level = models.CharField(max_length=255, verbose_name="Nivel")
    grade = models.CharField(max_length=255, verbose_name="Grado")
    parallel = models.CharField(max_length=255, verbose_name="Paralelo")
    capacity = models.IntegerField(verbose_name="Capacidad")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )
    updated_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Actualización"
    )

    class Meta:
        app_label = "academic"
        verbose_name = "Sección"
        verbose_name_plural = "Secciones"

    def __str__(self):
        return f"{self.school_year.institution.name} - {self.grade} {self.parallel}"
