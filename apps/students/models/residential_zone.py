from django.db import models


class ResidentialZone(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "students"
        verbose_name = "Zona Residencial"
        verbose_name_plural = "Zonas Residenciales"
        ordering = ["name"]

    def __str__(self):
        return self.name