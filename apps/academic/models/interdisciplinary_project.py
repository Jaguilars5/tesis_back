from django.db import models
from apps.core.models import TimeStampedModel


class InterdisciplinaryProject(TimeStampedModel):
    academic_period = models.ForeignKey(
        "academic.AcademicPeriod",
        on_delete=models.CASCADE,
        related_name="interdisciplinary_projects",
        verbose_name="Período Académico",
    )
    subject_offerings = models.ManyToManyField(
        "academic.SubjectOffering",
        through="academic.SubjectProject",
        verbose_name="Ofertas de Materia",
    )
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(null=True, blank=True, verbose_name="Descripción")
    start_date = models.DateField(verbose_name="Fecha de inicio")
    delivery_date = models.DateField(verbose_name="Fecha de entrega")
    product_max_score = models.DecimalField(
        max_digits=5, decimal_places=2, default=10.00,
        verbose_name="Puntaje máximo del producto",
    )
    presentation_max_score = models.DecimalField(
        max_digits=5, decimal_places=2, default=10.00,
        verbose_name="Puntaje máximo de la presentación",
    )
    product_rubric = models.TextField(null=True, blank=True, verbose_name="Rúbrica del producto")
    presentation_rubric = models.TextField(null=True, blank=True, verbose_name="Rúbrica de la presentación")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "academic"
        verbose_name = "Proyecto Interdisciplinario"
        verbose_name_plural = "Proyectos Interdisciplinarios"
        ordering = ["-start_date"]

    def __str__(self):
        return self.title
