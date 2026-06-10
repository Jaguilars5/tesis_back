from django.db import models


class RecoveryProcessStatus(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "grading"
        verbose_name = "Estado de Proceso de Recuperación"
        verbose_name_plural = "Estados de Procesos de Recuperación"
        ordering = ["name"]

    def __str__(self):
        return self.name
