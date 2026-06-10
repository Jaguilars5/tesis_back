from django.db import models
from apps.core.models import TimeStampedModel


class AuditLog(TimeStampedModel):
    user = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True,
        verbose_name="Usuario",
    )
    action = models.CharField(max_length=20, choices=[
        ("CREATE", "Creación"),
        ("UPDATE", "Modificación"),
        ("DELETE", "Eliminación"),
        ("RECOVER", "Recuperación"),
    ], verbose_name="Acción")
    model_name = models.CharField(max_length=100, verbose_name="Modelo")
    record_id = models.CharField(max_length=36, verbose_name="ID del Registro")
    changes = models.JSONField(default=dict, blank=True, verbose_name="Cambios")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Dirección IP")
    user_agent = models.CharField(max_length=255, blank=True, verbose_name="User-Agent")

    class Meta:
        app_label = "core"
        verbose_name = "Bitácora de Auditoría"
        verbose_name_plural = "Bitácoras de Auditoría"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["model_name", "record_id"]),
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["action", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.action} - {self.model_name}#{self.record_id} ({self.user})"
