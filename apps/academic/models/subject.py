from django.db import models


class Subject(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nombre de la Materia")
    code = models.CharField(max_length=100, unique=True, verbose_name="Código")
    active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de Actualización"
    )

    class Meta:
        app_label = "academic"
        verbose_name = "Materia"
        verbose_name_plural = "Materias"

    def __str__(self):
        return self.name
