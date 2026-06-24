from django.db import models

from apps.core.models import TimeStampedModel


class AcademicSublevel(TimeStampedModel):
    academic_level = models.ForeignKey(
        "institutions_academic_level.AcademicLevel",
        on_delete=models.CASCADE,
        verbose_name="Nivel Acad\u00e9mico",
        related_name="sublevels",
    )
    code = models.CharField(max_length=20, unique=True, verbose_name="C\u00f3digo")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripci\u00f3n")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "institutions_academic_sublevel"
        verbose_name = "Subnivel Acad\u00e9mico"
        verbose_name_plural = "Subniveles Acad\u00e9micos"
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def academic_level_name(self):
        return self.academic_level.name if self.academic_level else None
