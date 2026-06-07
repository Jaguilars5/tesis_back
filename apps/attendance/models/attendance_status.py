from django.db import models


class AttendanceStatus(models.Model):
    TIPO_CHOICES = [
        ("POSITIVO", "Positivo"),
        ("NEGATIVO", "Negativo"),
    ]

    code = models.CharField(max_length=10, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    tipo = models.CharField(
        max_length=10,
        choices=TIPO_CHOICES,
        null=True,
        blank=True,
        verbose_name="Tipo",
        help_text="Clasificación del estado (POSITIVO = presente/puntual, NEGATIVO = ausencia/retraso)",
    )

    class Meta:
        app_label = "attendance"
        verbose_name = "Estado de Asistencia"
        verbose_name_plural = "Estados de Asistencia"
        ordering = ["name"]

    def __str__(self):
        return self.name
