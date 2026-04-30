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

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    student = models.ForeignKey(
        "students.Student", on_delete=models.CASCADE, help_text="Estudiante involucrado"
    )
    reported_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        help_text="Usuario que realiza el reporte",
    )
    academic_period = models.ForeignKey(
        "academic.Academic_Period",
        on_delete=models.CASCADE,
        help_text="Período académico correspondiente",
    )
    incident_date = models.DateField(help_text="Fecha en que ocurrió el incidente")
    category = models.CharField(
        max_length=30, choices=CATEGORY_CHOICES, help_text="Tipo de incidente"
    )
    severity = models.IntegerField(
        choices=SEVERITY_CHOICES, help_text="Nivel de gravedad del incidente"
    )
    description = models.TextField(
        null=True, blank=True, help_text="Descripción detallada del suceso"
    )
    family_notified = models.BooleanField(
        default=False, help_text="Indica si se ha comunicado a la familia"
    )
    
    # Sync & Audit Fields
    sync_status = models.CharField(max_length=20, default="pending")
    synced_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    sync_version = models.PositiveIntegerField(
        default=0, help_text="Versión para control de sincronización"
    )
    device_origin = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        help_text="Identificador del dispositivo de origen",
    )

    class Meta:
        app_label = "grading"

    def __str__(self):
        return f"{self.student.names} - {self.category} ({self.incident_date})"

