from django.db import models
from apps.core.models import TimeStampedModel


class TeacherSubjectSection(TimeStampedModel):
    user = models.ForeignKey(
        "iam.User", on_delete=models.CASCADE, verbose_name="Docente"
    )
    subject_offering = models.ForeignKey(
        "academic.SubjectOffering",
        on_delete=models.CASCADE,
        verbose_name="Oferta de Materia",
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    class Meta:
        app_label = "academic"
        verbose_name = "Docente-Materia-Sección"
        verbose_name_plural = "Docentes-Materias-Secciones"
        unique_together = [("user", "subject_offering")]
        indexes = [
            models.Index(fields=["user", "is_active"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.subject_offering}"
