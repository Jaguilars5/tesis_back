from django.db import models


class SubjectProject(models.Model):
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

    class Meta:
        app_label = "academic"
        verbose_name = "Asignatura del Proyecto"
        verbose_name_plural = "Asignaturas del Proyecto"
        unique_together = ("interdisciplinary_project", "subject_offering")

    def __str__(self):
        return f"{self.interdisciplinary_project.title} - {self.subject_offering}"
