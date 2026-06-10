from django.db import models
from apps.core.models import TimeStampedModel


class SubjectOffering(TimeStampedModel):
    school_year = models.ForeignKey(
        "institutions.SchoolYear",
        on_delete=models.CASCADE,
        verbose_name="Año Escolar",
    )
    section = models.ForeignKey(
        "institutions.Section",
        on_delete=models.CASCADE,
        verbose_name="Sección",
    )
    subject_academic_config = models.ForeignKey(
        "academic.SubjectAcademicConfig",
        on_delete=models.CASCADE,
        verbose_name="Configuración de Materia",
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "academic"
        verbose_name = "Oferta de Materia"
        verbose_name_plural = "Ofertas de Materias"
        unique_together = ("school_year", "section", "subject_academic_config")
        indexes = [
            models.Index(fields=["section", "school_year"]),
        ]

    def __str__(self):
        return f"{self.school_year} - {self.section} - {self.subject_academic_config}"
