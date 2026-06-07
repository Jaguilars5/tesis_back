from django.db import models


class IncidentType(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(null=True, blank=True, verbose_name="Descripción")

    class Meta:
        app_label = "attendance"
        verbose_name = "Tipo de Incidente"
        verbose_name_plural = "Tipos de Incidente"
        ordering = ["name"]

    def __str__(self):
        return self.name
