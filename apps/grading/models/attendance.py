from django.db import models
import uuid


class Attendance(models.Model):
    """
    Registro de asistencia de un estudiante a una clase específica.

    student: Estudiante cuya asistencia se registra
    teacher_subject_section: Clase (docente-materia-sección) a la que corresponde la asistencia
    academic_period: Período académico vigente
    date: Fecha de la clase
    status: Estado de la asistencia (Presente, Ausente, etc.)
    observation: Notas adicionales del docente sobre la asistencia
    device_origin: Dispositivo donde se tomó la asistencia
    sync_version: Control de versiones para sincronización
    """

    STATUS_CHOICES = [
        ("P", "Presente"),
        ("A", "Ausente"),
        ("T", "Tardanza"),
        ("J", "Justificado"),
    ]

    uuid = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, verbose_name="UUID"
    )
    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        verbose_name="Estudiante",
        help_text="Estudiante evaluado",
    )
    teacher_subject_section = models.ForeignKey(
        "academic.Teacher_Subject_Section",
        on_delete=models.CASCADE,
        verbose_name="Clase",
        help_text="Clase o sección a la que asiste",
    )
    academic_period = models.ForeignKey(
        "academic.Academic_Period",
        on_delete=models.CASCADE,
        verbose_name="Período Académico",
        help_text="Período académico correspondiente",
    )
    date = models.DateField(
        verbose_name="Fecha", help_text="Fecha en la que se registra la asistencia"
    )
    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        verbose_name="Estado",
        help_text="Estado de la asistencia",
    )
    observation = models.TextField(
        null=True,
        blank=True,
        verbose_name="Observaciones",
        help_text="Observaciones adicionales",
    )

    # Sync & Audit Fields
    sync_status = models.CharField(
        max_length=20, default="pending", verbose_name="Estado de Sincronización"
    )
    synced_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Sincronizado en"
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
        help_text="Versión para control de sincronización",
    )
    device_origin = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        verbose_name="Dispositivo de Origen",
        help_text="Identificador del dispositivo de origen",
    )

    class Meta:
        app_label = "grading"
        verbose_name = "Asistencia"
        verbose_name_plural = "Asistencias"
        unique_together = ("student", "teacher_subject_section", "date")
        indexes = [
            models.Index(fields=["student", "academic_period"]),
            models.Index(fields=["teacher_subject_section", "date"]),
        ]

    def __str__(self):
        return f"{self.student.names} - {self.date} - {self.status}"
