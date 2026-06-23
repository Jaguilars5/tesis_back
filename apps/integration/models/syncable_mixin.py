import uuid
from django.db import models
from django.db.models import F
from django.utils import timezone


class SyncStatusChoices(models.TextChoices):
    PENDING = "PENDING", "Pendiente de sincronizar"
    PROCESSING = "PROCESSING", "En procesamiento"
    SYNCED = "SYNCED", "Sincronizado"
    ERROR = "ERROR", "Error de sincronización"
    CONFLICT = "CONFLICT", "Conflicto detectado"


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
