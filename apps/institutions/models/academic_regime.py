from django.db import models


class AcademicRegime(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")

    class Meta:
        app_label = "institutions"
        verbose_name = "Régimen Académico"
        verbose_name_plural = "Regímenes Académicos"
        ordering = ["name"]

    def __str__(self):
        return self.name
