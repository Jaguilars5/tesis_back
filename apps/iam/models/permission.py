from django.db import models
from apps.core.models import TimeStampedModel


class Permission(TimeStampedModel):
    code = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Código del Permiso",
        help_text="Formato: '<app>.<acción>', ej: 'grading.create_note'",
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Descripción",
        help_text="Descripción legible del permiso",
    )
    module = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Módulo",
        help_text="Módulo asociado (grading, academic, etc)",
    )
    class Meta:
        app_label = "iam"
        verbose_name = "Permiso"
        verbose_name_plural = "Permisos"
        ordering = ["code"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["module"]),
        ]

    def __str__(self):
        return self.code
