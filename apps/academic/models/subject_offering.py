from django.db import models


class SubjectOffering(models.Model):
    school_year = models.ForeignKey(
        "institutions.School_Year",
        on_delete=models.CASCADE,
        verbose_name="Año Escolar",
    )
    section = models.ForeignKey(
        "academic.Section",
        on_delete=models.CASCADE,
        verbose_name="Sección",
    )
    subject_academic_config = models.ForeignKey(
        "academic.SubjectAcademicConfig",
        on_delete=models.CASCADE,
        verbose_name="Configuración de Materia",
    )
    active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "academic"
        verbose_name = "Oferta de Materia"
        verbose_name_plural = "Ofertas de Materias"
        unique_together = ("school_year", "section", "subject_academic_config")

    def __str__(self):
        return f"{self.school_year} - {self.section} - {self.subject_academic_config}"
