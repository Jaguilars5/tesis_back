from django.db import models
from apps.core.models import TimeStampedModel


class GradeChangeHistory(TimeStampedModel):
    student_note = models.ForeignKey(
        "grading.StudentNote",
        on_delete=models.CASCADE,
        related_name="change_history",
        verbose_name="Nota",
    )
    modified_by_user = models.ForeignKey(
        "iam.User",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Modificado por",
    )
    created_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="grade_changes_created", verbose_name="Creado por",
    )
    previous_score = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Nota Anterior"
    )
    new_score = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Nota Nueva"
    )
    previous_qualitative = models.ForeignKey(
        "grading.QualitativeScale",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="previous_grade_changes",
        verbose_name="Escala Cualitativa Anterior",
    )
    new_qualitative = models.ForeignKey(
        "grading.QualitativeScale",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="new_grade_changes",
        verbose_name="Nueva Escala Cualitativa",
    )
    reason = models.TextField(verbose_name="Razón del Cambio")
    reason_code = models.CharField(max_length=30, blank=True, verbose_name="Código de Razón")
    origin = models.CharField(max_length=20, choices=[
        ("MANUAL", "Manual"),
        ("IMPORT", "Importación"),
        ("SYNC", "Sincronización"),
    ], default="MANUAL", verbose_name="Origen")
    device_origin = models.CharField(max_length=40, null=True, blank=True, verbose_name="Dispositivo de Origen")
    modified_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Modificado en"
    )

    class Meta:
        app_label = "grading"
        verbose_name = "Historial de Cambio de Calificación"
        verbose_name_plural = "Historiales de Cambio de Calificación"
        ordering = ["-modified_at"]
        indexes = [
            models.Index(fields=["student_note", "modified_at"]),
            models.Index(fields=["modified_by_user", "modified_at"]),
        ]

    def __str__(self):
        return f"{self.student_note} - {self.previous_score} → {self.new_score}"
