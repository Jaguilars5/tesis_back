from django.db import models


class AcademicGrade(models.Model):
    academic_level = models.ForeignKey(
        "institutions.AcademicLevel",
        on_delete=models.CASCADE,
        verbose_name="Nivel Académico",
    )
    name = models.CharField(max_length=100, verbose_name="Nombre del Grado")
    sequence_order = models.IntegerField(verbose_name="Orden")
    active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "institutions"
        verbose_name = "Grado Académico"
        verbose_name_plural = "Grados Académicos"
        ordering = ["sequence_order"]

    def __str__(self):
        return f"{self.academic_level.name} - {self.name}"
