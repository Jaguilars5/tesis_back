from django.db import models
from apps.core.models import TimeStampedModel


class AcademicSublevel(TimeStampedModel):
    academic_level = models.ForeignKey(
        "institutions.AcademicLevel",
        on_delete=models.CASCADE,
        verbose_name="Nivel Académico",
        related_name="sublevels",
    )
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "institutions"
        verbose_name = "Subnivel Académico"
        verbose_name_plural = "Subniveles Académicos"
        ordering = ["name"]

    def __str__(self):
        return f"{self.academic_level.name} - {self.name}"
