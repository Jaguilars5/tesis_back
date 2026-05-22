from django.db import models


class Classroom(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre del Salón")
    room_type = models.ForeignKey(
        "institutions.RoomType",
        on_delete=models.CASCADE,
        verbose_name="Tipo de Sala",
        null=True,
    )
    capacity = models.IntegerField(verbose_name="Capacidad")
    active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "institutions"
        verbose_name = "Salón"
        verbose_name_plural = "Salones"

    def __str__(self):
        return f"{self.name} ({self.room_type})"
