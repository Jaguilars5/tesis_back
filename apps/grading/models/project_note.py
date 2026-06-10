from django.db import models
from apps.core.models import TimeStampedModel
from apps.integration.models.syncable_mixin import SyncableModel


class ProjectNote(TimeStampedModel, SyncableModel):
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        related_name="project_notes",
        verbose_name="Matrícula",
    )
    interdisciplinary_project = models.ForeignKey(
        "academic.InterdisciplinaryProject",
        on_delete=models.CASCADE,
        related_name="project_notes",
        verbose_name="Proyecto Interdisciplinario",
    )
    product_score = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Nota del producto"
    )
    presentation_score = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Nota de exposición"
    )
    final_score = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Nota final"
    )
    observation = models.TextField(null=True, blank=True, verbose_name="Observación")

    class Meta:
        app_label = "grading"
        verbose_name = "Nota de Proyecto"
        verbose_name_plural = "Notas de Proyectos"
        unique_together = ("enrollment", "interdisciplinary_project")
        indexes = [
            models.Index(fields=["interdisciplinary_project"]),
        ]

    def __str__(self):
        return f"{self.enrollment} - {self.interdisciplinary_project.title} ({self.final_score})"
