import uuid
from django.db import models
from apps.core.models import TimeStampedModel


class SyncQueue(TimeStampedModel):
    uuid = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, verbose_name="UUID",
    )
    user = models.ForeignKey(
        "iam.User",
        on_delete=models.CASCADE,
        verbose_name="Usuario origen",
    )
    source_table = models.CharField(
        max_length=100, verbose_name="Tabla Origen",
    )
    record_uuid = models.CharField(
        max_length=36, verbose_name="UUID del Registro",
    )
    operation = models.ForeignKey("integration.SyncOperation", on_delete=models.PROTECT, verbose_name="Operación")
    payload = models.JSONField(
        verbose_name="Payload", default=dict, blank=True,
    )
    attempts = models.PositiveIntegerField(default=0, verbose_name="Intentos")
    last_error = models.TextField(null=True, blank=True, verbose_name="Último Error")
    status = models.ForeignKey("integration.SyncStatus", on_delete=models.PROTECT, null=True, blank=True, verbose_name="Estado")
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name="Procesada en")

    class Meta:
        app_label = "integration"
        verbose_name = "Cola de Sincronización"
        verbose_name_plural = "Cola de Sincronización"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["source_table", "record_uuid"]),
            models.Index(fields=["user", "status"]),
        ]

    def __str__(self):
        return f"{self.operation} — {self.source_table} ({self.status})"
