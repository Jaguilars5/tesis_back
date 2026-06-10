from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import models
from apps.core.models import TimeStampedModel
from apps.integration.models.syncable_mixin import SyncableModel


class StudentNote(TimeStampedModel, SyncableModel):
    """
    NOTA_ACTIVIDAD — Calificación individual de un estudiante en una actividad.
    Entidad de mayor volumen; soporte offline-first.
    """

    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        verbose_name="Matrícula",
    )
    evaluative_activity = models.ForeignKey(
        "grading.EvaluativeActivity",
        on_delete=models.CASCADE,
        verbose_name="Actividad Evaluativa",
        null=True, blank=True,
    )
    grade_type = models.ForeignKey(
        "grading.GradeType",
        on_delete=models.PROTECT,
        verbose_name="Tipo de Calificación",
        null=True, blank=True,
    )
    grading_mode = models.CharField(
        max_length=20,
        choices=[
            ("NUMERIC", "Cuantitativa"),
            ("QUALITATIVE", "Cualitativa"),
        ],
        default="NUMERIC",
        verbose_name="Modo de Calificación",
        help_text="Define si la nota es numérica o cualitativa",
    )
    qualitative_scale = models.ForeignKey(
        "grading.QualitativeScale",
        on_delete=models.PROTECT,
        null=True, blank=True,
        verbose_name="Escala Cualitativa",
        help_text="Escala cualitativa equivalente a la nota (si aplica)",
    )
    numeric_score = models.DecimalField(
        max_digits=5, decimal_places=2,
        verbose_name="Puntuación Numérica",
        help_text="Calificación numérica obtenida (escala 1-10)",
        null=True, blank=True,
    )
    manually_overridden = models.BooleanField(
        default=False, verbose_name="Anulada Manualmente"
    )
    teacher_observation = models.TextField(
        null=True, blank=True, verbose_name="Observación del Docente"
    )
    created_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="student_notes_created", verbose_name="Creado por",
    )
    modified_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="student_notes_modified", verbose_name="Modificado por",
    )

    class Meta:
        app_label = "grading"
        verbose_name = "Nota de Actividad"
        verbose_name_plural = "Notas de Actividades"
        unique_together = [("enrollment", "evaluative_activity")]
        indexes = [
            models.Index(fields=["enrollment", "evaluative_activity"]),
            models.Index(fields=["evaluative_activity", "numeric_score"]),
            models.Index(fields=["sync_status"]),
            models.Index(fields=["enrollment", "sync_status"]),
        ]

    def clean(self):
        super().clean()
        if self.grading_mode == "NUMERIC" and not self.numeric_score:
            raise ValidationError(
                {"numeric_score": "numeric_score es requerido para calificación cuantitativa"}
            )
        if self.grading_mode == "QUALITATIVE" and not self.qualitative_scale:
            raise ValidationError(
                {"qualitative_scale": "qualitative_scale es requerido para calificación cualitativa"}
            )
        if self.evaluative_activity_id and self.numeric_score is not None:
            max_value = self.evaluative_activity.max_score
            if self.numeric_score < 0 or self.numeric_score > max_value:
                raise ValidationError(
                    {"numeric_score": f"La nota debe estar entre 0 y {max_value}"}
                )

    def calculate_normalized_value(self):
        if not self.evaluative_activity_id:
            return self.numeric_score
        max_value = Decimal(self.evaluative_activity.max_score)
        if max_value == 0:
            return Decimal("0.00")
        normalized = (Decimal(self.numeric_score) / max_value) * Decimal("10")
        return normalized.quantize(Decimal("0.01"))

    def __str__(self):
        return f"{self.enrollment} - {self.evaluative_activity} (score: {self.numeric_score})"
