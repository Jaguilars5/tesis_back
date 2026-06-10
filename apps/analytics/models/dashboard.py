from django.db import models
from apps.core.models import TimeStampedModel


class DashboardMetric(TimeStampedModel):
    academic_period = models.ForeignKey(
        "academic.AcademicPeriod", on_delete=models.CASCADE,
        verbose_name="Período Académico",
    )
    section = models.ForeignKey(
        "institutions.Section", on_delete=models.CASCADE, null=True, blank=True,
        verbose_name="Sección",
    )
    academic_grade = models.ForeignKey(
        "institutions.AcademicGrade", on_delete=models.CASCADE, null=True, blank=True,
        verbose_name="Grado Académico",
    )
    metric_type = models.CharField(max_length=50, verbose_name="Tipo de Métrica")
    metric_value = models.JSONField(default=dict, verbose_name="Valor de la Métrica")
    metric_schema_version = models.CharField(max_length=10, blank=True, default="1.0", verbose_name="Versión del Esquema")
    calculated_at = models.DateTimeField(auto_now_add=True, verbose_name="Calculado en")

    class Meta:
        app_label = "analytics"
        verbose_name = "Métrica de Dashboard"
        verbose_name_plural = "Métricas de Dashboard"
        unique_together = [("academic_period", "section", "metric_type")]
        indexes = [
            models.Index(fields=["academic_period", "metric_type"]),
            models.Index(fields=["calculated_at"]),
        ]

    def __str__(self):
        return f"{self.metric_type} - {self.academic_period}"
