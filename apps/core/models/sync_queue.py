import uuid
from django.db import models


class SyncQueue(models.Model):
    """
    COLA_SINCRONIZACION — Cola de operaciones pendientes de sincronización offline→servidor.
    Alta frecuencia de escritura; se consume y limpia continuamente.
    """

    uuid = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, verbose_name="UUID",
        help_text="UUID único de esta operación de sincronización",
    )
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        verbose_name="Usuario origen",
        help_text="Usuario que originó la operación offline",
    )
    source_table = models.CharField(
        max_length=100,
        verbose_name="Tabla Origen",
        help_text="Nombre de la tabla que originó la operación pendiente",
    )
    record_uuid = models.CharField(
        max_length=36,
        verbose_name="UUID del Registro",
        help_text="UUID del registro en la tabla de origen",
    )
    operation = models.CharField(
        max_length=10,
        choices=[
            ("INSERT", "Insertar"),
            ("UPDATE", "Actualizar"),
            ("DELETE", "Eliminar"),
        ],
        verbose_name="Operación",
        help_text="Tipo de operación pendiente: INSERT, UPDATE o DELETE",
    )
    payload = models.JSONField(
        verbose_name="Payload",
        default=dict,
        blank=True,
        help_text="Datos completos del registro a sincronizar en formato JSON",
    )
    attempts = models.PositiveIntegerField(
        default=0,
        verbose_name="Intentos",
        help_text="Número de intentos fallidos de sincronización",
    )
    last_error = models.TextField(
        null=True, blank=True,
        verbose_name="Último Error",
        help_text="Descripción del último error de sincronización",
    )
    status = models.CharField(
        max_length=10,
        choices=[
            ("PENDIENTE", "Pendiente"),
            ("PROCESADO", "Procesado"),
            ("ERROR", "Error"),
        ],
        default="PENDIENTE",
        verbose_name="Estado",
        help_text="Estado actual de la operación: PENDIENTE, PROCESADO o ERROR",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Creada en",
        help_text="Fecha y hora en que se generó la operación offline",
    )
    processed_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name="Procesada en",
        help_text="Fecha y hora en que fue procesada exitosamente",
    )

    class Meta:
        app_label = "core"
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
