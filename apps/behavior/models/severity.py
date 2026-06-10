from django.db import models


class Severity(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    numeric_level = models.IntegerField(verbose_name="Nivel Numérico")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "behavior"
        verbose_name = "Severidad"
        verbose_name_plural = "Severidades"
        ordering = ["numeric_level"]

    def __str__(self):
        return self.name