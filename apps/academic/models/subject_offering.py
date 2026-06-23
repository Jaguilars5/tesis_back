from django.db import models
from django.db.models import UniqueConstraint
from apps.core.models import TimeStampedModel


class SubjectOffering(TimeStampedModel):
    """Representa la oferta de una materia en una sección durante un año escolar."""

    section = models.ForeignKey(
        "institutions.Section",
        on_delete=models.CASCADE,
        related_name="subject_offerings",
        verbose_name="Sección",
    )
    subject_academic_config = models.ForeignKey(
        "academic.SubjectAcademicConfig",
        on_delete=models.CASCADE,
        related_name="offerings",
        verbose_name="Configuración de Materia",
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "academic"
        verbose_name = "Oferta de Materia"
        verbose_name_plural = "Ofertas de Materias"
        constraints = [
            UniqueConstraint(
                fields=["section", "subject_academic_config"],
                name="unique_section_subject_config",
            ),
        ]

    def __str__(self):
        if self.subject_academic_config_id and self.section_id:
            subject_name = self.subject_academic_config.subject.name
            return f"{subject_name} - {self.section}"
        return f"Offering #{self.pk}"

    @property
    def school_year(self):
        return self.section.school_year
