from django.db import models
import uuid


class ConductIncident(models.Model):
    """
    Registro de incidentes de comportamiento de un estudiante.

    student: Estudiante involucrado en el incidente
    reported_by: Usuario que reporta el incidente (docente, inspector, etc.)
    academic_period: Período académico en el que ocurre
    incident_date: Fecha del incidente
    category: Categoría del incidente (disciplina, académica, etc.)
    severity: Nivel de gravedad (Leve, Moderado, Grave)
    description: Detalle de lo sucedido
    family_notified: Indica si se notificó a los representantes
    device_origin: Dispositivo donde se registró el incidente
    sync_version: Control de versiones para sincronización
    """

    CATEGORY_CHOICES = [
        ("disciplina", "Disciplina"),
        ("academica", "Académica"),
        ("social", "Social"),
        ("asistencia", "Asistencia"),
    ]

    SEVERITY_CHOICES = [(1, "Leve"), (2, "Moderado"), (3, "Grave")]

    uuid = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, verbose_name="UUID"
    )
    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        verbose_name="Estudiante",
        help_text="Estudiante involucrado",
    )
    reported_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Reportado por",
        help_text="Usuario que realiza el reporte",
    )
    academic_period = models.ForeignKey(
        "academic.Academic_Period",
        on_delete=models.CASCADE,
        verbose_name="Período Académico",
        help_text="Período académico correspondiente",
    )
    incident_date = models.DateField(
        verbose_name="Fecha del Incidente",
        help_text="Fecha en que ocurrió el incidente",
    )
    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        verbose_name="Categoría",
        help_text="Tipo de incidente",
    )
    severity = models.IntegerField(
        choices=SEVERITY_CHOICES,
        verbose_name="Gravedad",
        help_text="Nivel de gravedad del incidente",
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="Descripción",
        help_text="Descripción detallada del suceso",
    )
    family_notified = models.BooleanField(
        default=False,
        verbose_name="Familia Notificada",
        help_text="Indica si se ha comunicado a la familia",
    )

    sync_status = models.CharField(
        max_length=20, default="pending", verbose_name="Estado de Sincronización"
    )
    synced_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Sincronizado el"
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
        verbose_name = "Incidente de Conducta"
        verbose_name_plural = "Incidentes de Conducta"

    def __str__(self):
        return f"{self.student.names} - {self.category} ({self.incident_date})"
