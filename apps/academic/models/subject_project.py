from django.db import models
from apps.core.models import TimeStampedModel


class SubjectProject(TimeStampedModel):
    interdisciplinary_project = models.ForeignKey(
        "academic.InterdisciplinaryProject",
        on_delete=models.CASCADE,
        related_name="subject_projects",
        verbose_name="Proyecto Interdisciplinario",
    )
    subject_offering = models.ForeignKey(
        "academic.SubjectOffering",
        on_delete=models.CASCADE,
        related_name="subject_projects",
        verbose_name="Oferta de Asignatura",
    )
    responsible_teacher = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True,
        verbose_name="Docente responsable",
    )

    class Meta:
        app_label = "academic"
        verbose_name = "Asignatura del Proyecto"
        verbose_name_plural = "Asignaturas del Proyecto"
        unique_together = ("interdisciplinary_project", "subject_offering")

    def __str__(self):
        return f"{self.interdisciplinary_project.title} - {self.subject_offering}"
