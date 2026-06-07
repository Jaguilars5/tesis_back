from django.db import models


class Section(models.Model):
    school_year = models.ForeignKey(
        "institutions.School_Year",
        on_delete=models.CASCADE,
        verbose_name="Año Escolar",
    )
    academic_grade = models.ForeignKey(
        "institutions.AcademicGrade",
        on_delete=models.CASCADE,
        verbose_name="Grado Académico",
        null=True,
    )
    parallel = models.CharField(max_length=255, verbose_name="Paralelo")
    capacity = models.IntegerField(verbose_name="Capacidad")
    active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "institutions"
        verbose_name = "Sección"
        verbose_name_plural = "Secciones"

    def __str__(self):
        if self.academic_grade:
            return (
                f"{self.school_year.name} - {self.academic_grade.name} {self.parallel}"
            )
        return f"{self.school_year.name} - {self.parallel}"
