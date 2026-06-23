from django.db import models
from apps.core.models import TimeStampedModel


class TeacherSubjectSection(TimeStampedModel):
    """Asocia un docente a una oferta de materia-sección."""

    user = models.ForeignKey(
        "iam.User", on_delete=models.CASCADE,
        related_name="teacher_assignments",
        verbose_name="Docente",
    )
    subject_offering = models.ForeignKey(
        "academic.SubjectOffering",
        on_delete=models.CASCADE,
        related_name="teacher_assignments",
        verbose_name="Oferta de Materia",
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "academic"
        verbose_name = "Docente-Materia-Sección"
        verbose_name_plural = "Docentes-Materias-Secciones"
        constraints = [
            models.UniqueConstraint(fields=["user", "subject_offering"], name="unique_teacher_subject"),
        ]
        indexes = [
            models.Index(fields=["user", "is_active"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.subject_offering}"
