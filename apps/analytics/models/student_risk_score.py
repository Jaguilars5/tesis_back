from django.db import models
from django.db.models import UniqueConstraint
from apps.core.models import TimeStampedModel


class StudentRiskScore(TimeStampedModel):
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        verbose_name="Matrícula",
    )
    academic_period = models.ForeignKey(
        "academic.AcademicPeriod",
        on_delete=models.CASCADE,
        verbose_name="Período Académico",
    )
    risk_score = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00, verbose_name="Puntaje de Riesgo",
    )
    risk_label = models.CharField(
        max_length=20, default="", verbose_name="Etiqueta de Riesgo",
    )
    model_version = models.CharField(
        max_length=50, default="", verbose_name="Versión del Modelo",
    )
    calculated_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Cálculo",
    )

    class Meta:
        app_label = "analytics"
        ordering = ["-calculated_at"]
        verbose_name = "Puntaje de Riesgo del Estudiante"
        verbose_name_plural = "Puntajes de Riesgo de los Estudiantes"
        constraints = [
            UniqueConstraint(
                fields=["enrollment", "academic_period", "model_version"],
                name="unique_enrollment_period_model_version"
            ),
        ]
        indexes = [
            models.Index(fields=["academic_period", "risk_label"]),
            models.Index(fields=["calculated_at"]),
        ]

    def __str__(self):
        return f"{self.enrollment} - {self.risk_label} ({self.risk_score})"