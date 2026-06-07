import uuid
from django.db import models


class ProjectNote(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="UUID")
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
    sync_status = models.CharField(max_length=20, default="pending", verbose_name="Estado de Sincronización")
    synced_at = models.DateTimeField(null=True, blank=True, verbose_name="Sincronizado el")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    sync_version = models.PositiveIntegerField(default=0, verbose_name="Versión de Sincronización")
    device_origin = models.CharField(max_length=40, null=True, blank=True, verbose_name="Dispositivo de Origen")

    class Meta:
        app_label = "grading"
        verbose_name = "Nota de Proyecto"
        verbose_name_plural = "Notas de Proyectos"
        unique_together = ("enrollment", "interdisciplinary_project")

    def __str__(self):
        return f"{self.enrollment} - {self.interdisciplinary_project.title} ({self.final_score})"
