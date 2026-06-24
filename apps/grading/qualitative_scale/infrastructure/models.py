from django.db import models

from apps.core.models import TimeStampedModel


class QualitativeScale(TimeStampedModel):
    """Representa una escala cualitativa de calificación."""

    code = models.CharField(max_length=10, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, blank=True, verbose_name="Nombre")
    description = models.TextField(verbose_name="Descripción")
    numeric_equivalence = models.DecimalField(
        max_digits=4, decimal_places=2, verbose_name="Equivalencia Numérica"
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "grading_qualitative_scale"
        verbose_name = "Escala Cualitativa"
        verbose_name_plural = "Escalas Cualitativas"
        ordering = ["-numeric_equivalence"]

    def __str__(self):
        return f"{self.code} — {self.description}"


class QualitativeScaleSublevel(models.Model):
    """Relación entre escala cualitativa y subnivel académico."""

    scale = models.ForeignKey(
        "grading_qualitative_scale.QualitativeScale",
        on_delete=models.CASCADE,
        related_name="sublevel_links",
        verbose_name="Escala Cualitativa",
    )
    sublevel = models.ForeignKey(
        "institutions_academic_sublevel.AcademicSublevel",
        on_delete=models.CASCADE,
        related_name="scale_links",
        verbose_name="Subnivel Académico",
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "grading_qualitative_scale"
        verbose_name = "Escala Cualitativa por Subnivel"
        verbose_name_plural = "Escalas Cualitativas por Subnivel"
        unique_together = [("scale", "sublevel")]

    def __str__(self):
        return f"{self.scale.code} - {self.sublevel.name}"
