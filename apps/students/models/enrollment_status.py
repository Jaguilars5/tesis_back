from django.db import models


class EnrollmentStatus(models.Model):
    code = models.CharField(max_length=10, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")

    class Meta:
        app_label = "students"
        verbose_name = "Estado de Matrícula"
        verbose_name_plural = "Estados de Matrícula"
        ordering = ["name"]

    def __str__(self):
        return self.name
