from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import models
import uuid


class StudentNote(models.Model):
    """
    NOTA_ACTIVIDAD — Calificación individual de un estudiante en una actividad.
    Entidad de mayor volumen; soporte offline-first.
    """

    uuid = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, verbose_name="UUID",
        help_text="Identificador único global para sincronización offline",
    )
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        verbose_name="Matrícula",
        null=True, blank=True,
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
    sync_status = models.CharField(
        max_length=20, default="PENDIENTE",
        verbose_name="Estado de Sincronización",
        help_text="PENDIENTE, SINCRONIZADO o ERROR",
    )
    synced_at = models.DateTimeField(null=True, blank=True, verbose_name="Sincronizado en")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
    sync_version = models.PositiveIntegerField(
        default=1, verbose_name="Versión de Sincronización",
        help_text="Número de versión para control de conflictos offline",
    )
    device_origin = models.CharField(
        max_length=40, null=True, blank=True, verbose_name="Dispositivo de Origen"
    )

    class Meta:
        app_label = "grading"
        verbose_name = "Nota de Actividad"
        verbose_name_plural = "Notas de Actividades"
        indexes = [
            models.Index(fields=["enrollment", "evaluative_activity"]),
            models.Index(fields=["sync_status"]),
        ]

    def clean(self):
        super().clean()
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
