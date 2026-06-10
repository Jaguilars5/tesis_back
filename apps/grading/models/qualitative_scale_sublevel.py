from django.db import models


class QualitativeScaleSublevel(models.Model):
    scale = models.ForeignKey(
        "grading.QualitativeScale",
        on_delete=models.CASCADE,
        related_name="sublevel_links",
        verbose_name="Escala Cualitativa",
    )
    sublevel = models.ForeignKey(
        "institutions.AcademicSublevel",
        on_delete=models.CASCADE,
        related_name="scale_links",
        verbose_name="Subnivel Académico",
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "grading"
        verbose_name = "Escala Cualitativa por Subnivel"
        verbose_name_plural = "Escalas Cualitativas por Subnivel"
        unique_together = [("scale", "sublevel")]

    def __str__(self):
        return f"{self.scale.code} - {self.sublevel.name}"