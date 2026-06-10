from django.db import models
from apps.core.models import TimeStampedModel


class RecoveryProcessType(TimeStampedModel):
    code = models.CharField(max_length=30, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    allows_improvement_eval = models.BooleanField(default=False, verbose_name="Permite evaluación de mejora")
    allows_suppletorio = models.BooleanField(default=False, verbose_name="Permite supletorio")
    min_grade_to_access = models.DecimalField(
        max_digits=4, decimal_places=2, default=7.00,
        verbose_name="Nota mínima para acceder",
    )
    max_recovery_attempts = models.IntegerField(default=1, verbose_name="Máximo de intentos")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "grading"
        verbose_name = "Tipo de Proceso de Recuperación"
        verbose_name_plural = "Tipos de Proceso de Recuperación"
        ordering = ["name"]

    def __str__(self):
        return self.name
