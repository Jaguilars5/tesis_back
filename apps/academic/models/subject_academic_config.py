from django.db import models


class SubjectAcademicConfig(models.Model):
    subject = models.ForeignKey(
        "academic.Subject",
        on_delete=models.CASCADE,
        verbose_name="Materia",
    )
    academic_grade = models.ForeignKey(
        "institutions.AcademicGrade",
        on_delete=models.CASCADE,
        verbose_name="Grado Académico",
    )
    weekly_hours = models.IntegerField(verbose_name="Horas Semanales")
    pedagogical_order = models.IntegerField(verbose_name="Orden Pedagógico")
    is_required = models.BooleanField(default=True, verbose_name="Obligatoria")
    active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "academic"
        verbose_name = "Configuración de Materia por Grado"
        verbose_name_plural = "Configuraciones de Materia por Grado"
        ordering = ["pedagogical_order"]

    def __str__(self):
        return f"{self.subject.name} - {self.academic_grade.name}"
