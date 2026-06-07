from django.db import models


class AcademicGrade(models.Model):
    SUBNIVEL_CHOICES = [
        ("INICIAL", "Inicial"),
        ("PREPARATORIA", "Preparatoria"),
        ("ELEMENTAL", "Elemental"),
        ("MEDIA", "Media"),
        ("SUPERIOR", "Superior"),
        ("BACHILLERATO", "Bachillerato"),
    ]

    academic_level = models.ForeignKey(
        "institutions.AcademicLevel",
        on_delete=models.CASCADE,
        verbose_name="Nivel Académico",
    )
    name = models.CharField(max_length=100, verbose_name="Nombre del Grado")
    subnivel = models.CharField(
        max_length=20,
        choices=SUBNIVEL_CHOICES,
        null=True,
        blank=True,
        verbose_name="Subnivel",
        help_text="Subnivel educativo del grado; determina reglas de evaluación diferenciadas",
    )
    sequence_order = models.IntegerField(verbose_name="Orden")
    active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "institutions"
        verbose_name = "Grado Académico"
        verbose_name_plural = "Grados Académicos"
        ordering = ["sequence_order"]

    def __str__(self):
        return f"{self.academic_level.name} - {self.name}"
