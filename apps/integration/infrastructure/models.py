import uuid
import hashlib
from django.db import models
from django.db.models import F
from django.utils import timezone
from apps.core.models import TimeStampedModel


class BatchStatusChoices(models.TextChoices):
    RECEIVED = "RECEIVED", "Recibido"
    QUEUED = "QUEUED", "Encolado"
    PROCESSING = "PROCESSING", "En procesamiento"
    COMPLETED = "COMPLETED", "Completado"
    FAILED = "FAILED", "Fallido"
    ROLLED_BACK = "ROLLED_BACK", "Revertido"


class SyncStatusChoices(models.TextChoices):
    PENDING = "PENDING", "Pendiente de sincronizar"
    PROCESSING = "PROCESSING", "En procesamiento"
    SYNCED = "SYNCED", "Sincronizado"
    ERROR = "ERROR", "Error de sincronización"
    CONFLICT = "CONFLICT", "Conflicto detectado"
    ROLLED_BACK = "ROLLED_BACK", "Revertido"


class SyncOperationChoices(models.TextChoices):
    CREATE = "CREATE", "Crear"
    UPDATE = "UPDATE", "Actualizar"
    DELETE = "DELETE", "Eliminar"


class SyncableModel(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, verbose_name="UUID")
    sync_status = models.CharField(
        max_length=20,
        choices=SyncStatusChoices.choices,
        default=SyncStatusChoices.PENDING,
        db_index=True,
        verbose_name="Estado de Sincronización",
    )
    sync_version = models.PositiveIntegerField(default=1, verbose_name="Versión de Sincronización")
    synced_at = models.DateTimeField(null=True, blank=True, verbose_name="Sincronizado en")
    device_origin = models.CharField(max_length=40, null=True, blank=True, verbose_name="Dispositivo de Origen")
    conflict_resolved = models.BooleanField(default=False, verbose_name="Conflicto Resuelto")
    conflict_notes = models.TextField(blank=True, default='', verbose_name="Notas de Conflicto")

    class Meta:
        abstract = True

    def increment_sync_version(self):
        self.sync_version = F("sync_version") + 1

    def mark_synced(self):
        self.sync_status = SyncStatusChoices.SYNCED
        self.synced_at = timezone.now()

    def mark_conflict(self):
        self.sync_status = SyncStatusChoices.CONFLICT

    def mark_error(self):
        self.sync_status = SyncStatusChoices.ERROR


class SyncBatch(TimeStampedModel):
    uuid = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, verbose_name="UUID",
    )
    client_batch_id = models.CharField(
        max_length=64, unique=True, db_index=True, verbose_name="ID del lote (cliente)",
    )
    user = models.ForeignKey(
        "iam.User",
        on_delete=models.CASCADE,
        verbose_name="Usuario origen",
    )
    status = models.CharField(
        max_length=20, choices=BatchStatusChoices.choices, default=BatchStatusChoices.RECEIVED,
        db_index=True, verbose_name="Estado del lote",
    )
    total_operations = models.PositiveIntegerField(default=0, verbose_name="Total de operaciones")
    completed_operations = models.PositiveIntegerField(default=0, verbose_name="Operaciones completadas")
    failed_operations = models.PositiveIntegerField(default=0, verbose_name="Operaciones fallidas")
    committed = models.BooleanField(default=False, verbose_name="Transacción commiteada")
    cached_response = models.JSONField(default=dict, blank=True, verbose_name="Respuesta cacheada")

    class Meta:
        app_label = "integration"
        verbose_name = "Lote de Sincronización"
        verbose_name_plural = "Lotes de Sincronización"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Batch {self.client_batch_id} — {self.status} ({self.total_operations} ops)"


class SyncQueue(TimeStampedModel):
    uuid = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, verbose_name="UUID",
    )
    batch = models.ForeignKey(
        SyncBatch, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="items", verbose_name="Lote",
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
    operation = models.CharField(
        max_length=20, choices=SyncOperationChoices.choices, verbose_name="Operación",
    )
    payload = models.JSONField(
        verbose_name="Payload", default=dict, blank=True,
    )
    previous_state = models.JSONField(
        default=dict, blank=True, verbose_name="Estado Anterior",
    )
    attempts = models.PositiveIntegerField(default=0, verbose_name="Intentos")
    max_attempts = models.PositiveIntegerField(default=5, verbose_name="Máximo de Intentos")
    last_error = models.TextField(blank=True, default='', verbose_name="Último Error")
    last_attempt_at = models.DateTimeField(null=True, blank=True, verbose_name="Último Intento")
    status = models.CharField(
        max_length=20, choices=SyncStatusChoices.choices, default=SyncStatusChoices.PENDING,
        db_index=True, verbose_name="Estado",
    )
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
    resolution_notes = models.TextField(blank=True, default='', verbose_name="Notas de resolución")

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
            op_code = self.operation if self.operation else "UNKNOWN"
            sync_version = (self.payload or {}).get("sync_version")
            if sync_version is not None:
                raw = f"{self.source_table}:{self.record_uuid}:{op_code}:{sync_version}"
            else:
                raw = f"{self.source_table}:{self.record_uuid}:{op_code}:{self.attempts}"
            self.idempotency_key = hashlib.sha256(raw.encode()).hexdigest()[:64]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.operation} — {self.source_table} ({self.status})"
