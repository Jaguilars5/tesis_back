from django.db import models
import uuid


class ConductIncident(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="UUID")
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        verbose_name="Matrícula",
        null=True,
    )
    reported_by_user = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Reportado por",
    )
    academic_period = models.ForeignKey(
        "academic.Academic_Period",
        on_delete=models.CASCADE,
        verbose_name="Período Académico",
    )
    incident_date = models.DateField(verbose_name="Fecha del Incidente")
    category = models.CharField(max_length=30, verbose_name="Categoría")
    severity = models.IntegerField(verbose_name="Gravedad")
    description = models.TextField(null=True, blank=True, verbose_name="Descripción")
    family_notified = models.BooleanField(default=False, verbose_name="Familia Notificada")

    sync_status = models.CharField(max_length=20, default="pending", verbose_name="Estado de Sincronización")
    synced_at = models.DateTimeField(null=True, blank=True, verbose_name="Sincronizado el")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
    sync_version = models.PositiveIntegerField(default=0, verbose_name="Versión de Sincronización")
    device_origin = models.CharField(max_length=40, null=True, blank=True, verbose_name="Dispositivo de Origen")

    class Meta:
        app_label = "grading"
        verbose_name = "Incidente de Conducta"
        verbose_name_plural = "Incidentes de Conducta"

    def __str__(self):
        return f"{self.enrollment} - {self.category} ({self.incident_date})"
