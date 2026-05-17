from django.db import models


class AttendanceStatus(models.Model):
    code = models.CharField(max_length=10, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")

    class Meta:
        app_label = "grading"
        verbose_name = "Estado de Asistencia"
        verbose_name_plural = "Estados de Asistencia"
        ordering = ["name"]

    def __str__(self):
        return self.name
