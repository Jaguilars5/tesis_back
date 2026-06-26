from django.db import models

from apps.core.models import TimeStampedModel


class AcademicGrade(TimeStampedModel):
    academic_sublevel = models.ForeignKey(
        "institutions_academic_sublevel.AcademicSublevel",
        on_delete=models.PROTECT,
        verbose_name="Subnivel Academico",
        null=True,
        blank=True,
    )
    code = models.CharField(max_length=50, blank=True, db_index=True, verbose_name="Codigo")
    name = models.CharField(max_length=100, verbose_name="Nombre del Grado")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "institutions_academic_grade"
        verbose_name = "Grado Academico"
        verbose_name_plural = "Grados Academicos"
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def academic_level(self):
        if self.academic_sublevel:
            return self.academic_sublevel.academic_level
        return None

    @property
    def academic_sublevel_name(self):
        return self.academic_sublevel.name if self.academic_sublevel else None
