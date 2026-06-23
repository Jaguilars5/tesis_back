from django.db import models
from apps.core.models import TimeStampedModel


class AcademicGrade(TimeStampedModel):
    academic_sublevel = models.ForeignKey(
        "institutions.AcademicSublevel",
        on_delete=models.PROTECT,
        verbose_name="Subnivel Académico",
        null=True,
        blank=True,
    )
    code = models.CharField(
        max_length=50, blank=True, db_index=True, verbose_name="Código"
    )
    name = models.CharField(max_length=100, verbose_name="Nombre del Grado")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "institutions"
        verbose_name = "Grado Académico"
        verbose_name_plural = "Grados Académicos"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}"

    @property
    def academic_level(self):
        if self.academic_sublevel:
            return self.academic_sublevel.academic_level
        return None
