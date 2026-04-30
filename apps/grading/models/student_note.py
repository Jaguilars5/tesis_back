from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
import uuid


class StudentNote(models.Model):
    """
    Registro de calificación de un estudiante para una actividad académica específica.

    student: Estudiante al que se le asigna la nota
    academic_activity: Actividad (Examen, Tarea, etc.) que se califica
    academic_period: Período académico (Primer Quimestre, etc.)
    teacher_subject_section: Relación docente-materia-sección
    note_value: Valor numérico de la calificación
    normalized_value: Valor normalizado (ej. base 10)
    observation: Comentarios adicionales sobre la nota
    sync_timestamp: Marca de tiempo para sincronización offline
    sync_status: Estado de sincronización (pending, synced)
    active: Indica si el registro es válido
    device_origin: Identificador del dispositivo donde se originó la nota
    sync_version: Versión incremental para control de concurrencia
    """

    uuid = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, verbose_name="UUID"
    )
    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        verbose_name="Estudiante",
        help_text="Estudiante evaluado",
    )
    academic_activity = models.ForeignKey(
        "academic.Academic_Activity",
        on_delete=models.CASCADE,
        verbose_name="Actividad Académica",
        help_text="Actividad académica evaluada",
    )
    academic_period = models.ForeignKey(
        "academic.Academic_Period",
        on_delete=models.CASCADE,
        verbose_name="Período Académico",
        help_text="Período académico correspondiente",
    )
    teacher_subject_section = models.ForeignKey(
        "academic.Teacher_Subject_Section",
        on_delete=models.CASCADE,
        verbose_name="Docente-Materia-Sección",
        help_text="Relación docente, materia y sección",
    )
    note_value = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Valor de la Nota",
        help_text="Valor obtenido en la actividad",
    )
    normalized_value = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Valor Normalizado",
        help_text="Valor de la nota normalizado (usualmente base 10)",
    )
    observation = models.TextField(
        null=True,
        blank=True,
        verbose_name="Observación",
        help_text="Observaciones o comentarios del docente",
    )

    sync_status = models.CharField(
        max_length=20,
        default="pending",
        verbose_name="Estado de Sincronización",
        help_text="Estado de sincronización con el servidor",
    )
    synced_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Sincronizado el"
    )
    active = models.BooleanField(
        default=True, verbose_name="Activo", help_text="Indica si la nota está activa"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de Actualización"
    )
    deleted_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Fecha de Eliminación"
    )
    sync_version = models.PositiveIntegerField(
        default=0,
        verbose_name="Versión de Sincronización",
        help_text="Versión para control de cambios",
    )
    device_origin = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        verbose_name="Dispositivo de Origen",
        help_text="ID o nombre del dispositivo de origen",
    )

    class Meta:
        app_label = "grading"
        verbose_name = "Nota de Estudiante"
        verbose_name_plural = "Notas de Estudiantes"
        unique_together = (
            "student",
            "academic_activity",
            "academic_period",
            "teacher_subject_section",
        )
        unique_together = (
            "student",
            "academic_activity",
            "academic_period",
            "teacher_subject_section",
        )

    def clean(self):
        """
        Validación de negocio para asegurar que la nota esté dentro de los límites
        permitidos por la actividad académica.
        """
        super().clean()
        if self.academic_activity_id and self.note_value is not None:
            max_value = self.academic_activity.value_max
            if self.note_value < 0 or self.note_value > max_value:
                raise ValidationError(
                    {"note_value": f"La nota debe estar entre 0 y {max_value}"}
                )

    def calculate_normalized_value(self):
        """
        Calcula el valor normalizado de la nota sobre una base de 10 puntos,
        proporcional al valor máximo de la actividad.
        """
        if not self.academic_activity_id:
            return self.normalized_value

        max_value = Decimal(self.academic_activity.value_max)
        if max_value == 0:
            return Decimal("0.00")

        normalized = (Decimal(self.note_value) / max_value) * Decimal("10")
        return normalized.quantize(Decimal("0.01"))

    def __str__(self):
        return (
            f"{self.student.names} - {self.academic_activity.name} - "
            f"{self.academic_period.name}"
        )
