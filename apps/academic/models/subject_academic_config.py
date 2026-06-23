from django.db import models
from apps.core.models import TimeStampedModel


class SubjectAcademicConfig(TimeStampedModel):
    """Configura cómo se enseña una materia en un grado académico específico."""

    academic_grade = models.ForeignKey(
        "institutions.AcademicGrade",
        on_delete=models.CASCADE,
        related_name="subject_academic_configs",
        verbose_name="Grado Académico",
    )
    subject = models.ForeignKey(
        "academic.Subject",
        on_delete=models.CASCADE,
        related_name="academic_configs",
        verbose_name="Materia",
    )
    weekly_hours = models.IntegerField(verbose_name="Horas Semanales")
    is_required = models.BooleanField(default=True, verbose_name="Obligatoria")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "academic"
        verbose_name = "Configuración de Materia por Grado"
        verbose_name_plural = "Configuraciones de Materia por Grado"
        ordering = ["subject"]
        constraints = [
            models.UniqueConstraint(
                fields=["subject", "academic_grade"],
                name="unique_subject_academic_grade",
            ),
        ]

    def __str__(self):
        return f"{self.subject.name} - {self.academic_grade.name}"
