from django.db import models


class Timing_Regime(models.Model):
    institution = models.ForeignKey(
        "institutions.Institution",
        on_delete=models.CASCADE,
        verbose_name="Institución",
        null=True,
    )
    name = models.CharField(max_length=100, verbose_name="Nombre del Régimen")
    description = models.TextField(null=True, blank=True, verbose_name="Descripción")
    active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "academic"
        verbose_name = "Régimen de Horario"
        verbose_name_plural = "Regímenes de Horario"

    def __str__(self):
        return f"{self.name}"
