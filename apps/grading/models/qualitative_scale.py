from django.db import models


class QualitativeScale(models.Model):
    code = models.CharField(max_length=10, unique=True, verbose_name="Código")
    description = models.TextField(verbose_name="Descripción")
    numeric_equivalence = models.DecimalField(
        max_digits=4, decimal_places=2, verbose_name="Equivalencia Numérica"
    )
    applicable_sublevel = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Subnivel Aplicable",
        help_text="Subnivel educativo al que aplica esta escala (ej: ELEMENTAL, MEDIA)",
    )

    class Meta:
        app_label = "grading"
        verbose_name = "Escala Cualitativa"
        verbose_name_plural = "Escalas Cualitativas"
        ordering = ["-numeric_equivalence"]

    def __str__(self):
        return f"{self.code} — {self.description}"
