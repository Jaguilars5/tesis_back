from django.db import models

from apps.core.models import TimeStampedModel


class NotificationType(models.TextChoices):
    ACTIVITY_CREATED = "ACTIVITY_CREATED", "Actividad creada"
    ACTIVITY_GRADED = "ACTIVITY_GRADED", "Actividad calificada"
    ATTENDANCE_CREATED = "ATTENDANCE_CREATED", "Asistencia registrada"
    INCIDENT_CREATED = "INCIDENT_CREATED", "Incidente de conducta"


class Notification(TimeStampedModel):
    """Notificación persistida para un usuario destinatario.

    Se complementa con la entrega en tiempo real (Socket.IO) y por correo;
    esta tabla mantiene el histórico y soporta el centro de notificaciones.
    """

    recipient = models.ForeignKey(
        "iam.User",
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="Destinatario",
    )
    notification_type = models.CharField(
        max_length=30,
        choices=NotificationType.choices,
        verbose_name="Tipo de Notificación",
    )
    title = models.CharField(max_length=200, verbose_name="Título")
    body = models.TextField(blank=True, default="", verbose_name="Cuerpo")
    data = models.JSONField(default=dict, blank=True, verbose_name="Datos")
    is_read = models.BooleanField(default=False, verbose_name="Leída")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="Leída en")

    class Meta:
        app_label = "core"
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "-created_at"]),
            models.Index(fields=["recipient", "is_read"]),
        ]

    def __str__(self):
        return f"{self.get_notification_type_display()} -> {self.recipient_id} ({self.title})"
