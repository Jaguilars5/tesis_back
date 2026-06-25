from django.db import models

from apps.core.models import TimeStampedModel


class Section(TimeStampedModel):
    school_year = models.ForeignKey(
        "institutions_school_year.SchoolYear",
        on_delete=models.CASCADE,
        verbose_name="Año Escolar",
    )
    academic_grade = models.ForeignKey(
        "institutions_academic_grade.AcademicGrade",
        on_delete=models.CASCADE,
        verbose_name="Grado Acad\u00e9mico",
        null=True,
    )
    code = models.CharField(max_length=50, blank=True, db_index=True, verbose_name="C\u00f3digo")
    parallel = models.CharField(max_length=255, verbose_name="Paralelo")
    capacity = models.IntegerField(verbose_name="Capacidad")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "institutions_section"
        verbose_name = "Secci\u00f3n"
        verbose_name_plural = "Secciones"
        unique_together = [("school_year", "academic_grade", "parallel")]

    def __str__(self):
        if self.academic_grade:
            return f"{self.academic_grade.name} {self.parallel}"
        return self.parallel
