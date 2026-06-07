from django.db import models


class GradeType(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    applies_to_sublevel = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Aplica a Subnivel",
        help_text="Subnivel(es) al que aplica esta calificación (ej: MEDIA,SUPERIOR,BACHILLERATO)",
    )

    class Meta:
        app_label = "grading"
        verbose_name = "Tipo de Calificación"
        verbose_name_plural = "Tipos de Calificación"
        ordering = ["name"]

    def __str__(self):
        return self.name
