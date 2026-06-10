import uuid
import hashlib
from django.db import models
from apps.core.models import TimeStampedModel


class SyncQueue(TimeStampedModel):
    uuid = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, verbose_name="UUID",
    )
    idempotency_key = models.CharField(
        max_length=64, unique=True, db_index=True, blank=True, verbose_name="Clave de Idempotencia",
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
    previous_state = models.JSONField(
        default=dict, blank=True, verbose_name="Estado Anterior",
    )
    attempts = models.PositiveIntegerField(default=0, verbose_name="Intentos")
    max_attempts = models.PositiveIntegerField(default=5, verbose_name="Máximo de Intentos")
    last_error = models.TextField(null=True, blank=True, verbose_name="Último Error")
    last_attempt_at = models.DateTimeField(null=True, blank=True, verbose_name="Último Intento")
    status = models.ForeignKey("integration.SyncStatus", on_delete=models.PROTECT, null=True, blank=True, verbose_name="Estado")
    conflict_detected = models.BooleanField(default=False, verbose_name="Conflicto Detectado")
    resolution_strategy = models.CharField(max_length=30, null=True, blank=True, verbose_name="Estrategia de Resolución")
    processed_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="sync_processed", verbose_name="Procesado por",
    )
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name="Procesada en")
    resolved_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="sync_resolved", verbose_name="Resuelto por",
    )
    resolution_notes = models.TextField(null=True, blank=True, verbose_name="Notas de resolución")

    class Meta:
        app_label = "integration"
        verbose_name = "Cola de Sincronización"
        verbose_name_plural = "Cola de Sincronización"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["source_table", "record_uuid"]),
            models.Index(fields=["user", "status"]),
            models.Index(fields=["conflict_detected", "status"]),
        ]

    def save(self, *args, **kwargs):
        if not self.idempotency_key:
            op_code = self.operation.code if self.operation else "UNKNOWN"
            raw = f"{self.source_table}:{self.record_uuid}:{op_code}:{self.attempts}"
            self.idempotency_key = hashlib.sha256(raw.encode()).hexdigest()[:64]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.operation} — {self.source_table} ({self.status})"
