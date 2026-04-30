from django.db import models


class Classroom(models.Model):
    institution = models.ForeignKey(
        "institutions.Institution", on_delete=models.CASCADE, verbose_name="Institución"
    )
    name = models.CharField(max_length=100, verbose_name="Nombre del Salón")
    room_type = models.CharField(max_length=50, verbose_name="Tipo de Sala")
    capacity = models.IntegerField(verbose_name="Capacidad")
    active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "institutions"
        verbose_name = "Salón"
        verbose_name_plural = "Salones"

    def __str__(self):
        return f"{self.name} ({self.room_type})"
