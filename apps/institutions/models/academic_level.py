from django.db import models


class AcademicLevel(models.Model):
    institution = models.ForeignKey(
        "institutions.Institution",
        on_delete=models.CASCADE,
        verbose_name="Institución",
    )
    name = models.CharField(max_length=100, verbose_name="Nombre del Nivel")
    active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "institutions"
        verbose_name = "Nivel Académico"
        verbose_name_plural = "Niveles Académicos"
        ordering = ["name"]

    def __str__(self):
        return self.name
