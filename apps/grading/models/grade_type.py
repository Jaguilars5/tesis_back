from django.db import models


class GradeType(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")

    class Meta:
        app_label = "grading"
        verbose_name = "Tipo de Nota"
        verbose_name_plural = "Tipos de Nota"
        ordering = ["name"]

    def __str__(self):
        return self.name
