from django.db import models
from apps.core.models import TimeStampedModel


class SyncSchemaVersion(TimeStampedModel):
    model_name = models.CharField(max_length=100, unique=True, verbose_name="Nombre del modelo")
    schema_version = models.PositiveIntegerField(default=1, verbose_name="Versión del esquema")
    fields_hash = models.CharField(max_length=64, verbose_name="Hash de campos")
    min_client_version = models.CharField(max_length=20, default="1.0.0", verbose_name="Versión mínima de cliente")

    class Meta:
        app_label = "integration"
        verbose_name = "Versión de Esquema de Sincronización"
        verbose_name_plural = "Versiones de Esquema de Sincronización"
        ordering = ["model_name"]

    def __str__(self):
        return f"{self.model_name} v{self.schema_version}"
