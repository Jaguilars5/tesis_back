from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import models
import uuid


class StudentNote(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="UUID")

    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        verbose_name="Matrícula",
        null=True, blank=True,
    )
    class_assignment = models.ForeignKey(
        "grading.ClassAssignment",
        on_delete=models.CASCADE,
        verbose_name="Tarea/Actividad",
        null=True, blank=True,
    )
    grade_type = models.ForeignKey(
        "grading.GradeType",
        on_delete=models.PROTECT,
        verbose_name="Tipo de Nota",
        null=True, blank=True,
    )
    qualitative_scale = models.ForeignKey(
        "grading.QualitativeScale",
        on_delete=models.PROTECT,
        null=True, blank=True,
        verbose_name="Escala Cualitativa",
    )
    numeric_score = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Nota Numérica",
        help_text="Valor obtenido en la actividad",
        null=True, blank=True,
    )
    manually_overridden = models.BooleanField(
        default=False, verbose_name="Modificado Manualmente"
    )
    teacher_observation = models.TextField(
        null=True, blank=True, verbose_name="Observación del Docente"
    )
    administrative_observation = models.TextField(
        null=True, blank=True, verbose_name="Observación Administrativa"
    )

    sync_status = models.CharField(max_length=20, default="pending", verbose_name="Estado de Sincronización")
    synced_at = models.DateTimeField(null=True, blank=True, verbose_name="Sincronizado el")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Eliminación")
    sync_version = models.PositiveIntegerField(default=0, verbose_name="Versión de Sincronización")
    device_origin = models.CharField(max_length=40, null=True, blank=True, verbose_name="Dispositivo de Origen")

    class Meta:
        app_label = "grading"
        verbose_name = "Nota de Estudiante"
        verbose_name_plural = "Notas de Estudiantes"

    def clean(self):
        super().clean()
        if self.class_assignment_id and self.numeric_score is not None:
            max_value = self.class_assignment.max_score
            if self.numeric_score < 0 or self.numeric_score > max_value:
                raise ValidationError(
                    {"numeric_score": f"La nota debe estar entre 0 y {max_value}"}
                )

    def calculate_normalized_value(self):
        if not self.class_assignment_id:
            return self.numeric_score
        max_value = Decimal(self.class_assignment.max_score)
        if max_value == 0:
            return Decimal("0.00")
        normalized = (Decimal(self.numeric_score) / max_value) * Decimal("10")
        return normalized.quantize(Decimal("0.01"))

    def __str__(self):
        return f"{self.enrollment} - {self.class_assignment} (score: {self.numeric_score})"
