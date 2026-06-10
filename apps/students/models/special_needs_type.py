from django.db import models


class SpecialNeedsType(models.Model):
    code = models.CharField(max_length=30, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "students"
        verbose_name = "Tipo de Necesidad Especial"
        verbose_name_plural = "Tipos de Necesidades Especiales"
        ordering = ["name"]

    def __str__(self):
        return self.name