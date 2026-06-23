from django.db import models
from apps.core.models import TimeStampedModel


class StudentRiskFactor(TimeStampedModel):
    student_risk_score = models.ForeignKey(
        "analytics.StudentRiskScore",
        on_delete=models.CASCADE,
        related_name="risk_factors",
        verbose_name="Puntaje de Riesgo",
    )
    risk_factor = models.ForeignKey(
        "analytics.RiskFactor",
        on_delete=models.CASCADE,
        verbose_name="Factor de Riesgo",
    )
    contribution_weight = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Peso de Contribución (%)"
    )

    class Meta:
        app_label = "analytics"
        verbose_name = "Factor de Riesgo del Estudiante"
        verbose_name_plural = "Factores de Riesgo de los Estudiantes"
        constraints = [
            models.UniqueConstraint(fields=["student_risk_score", "risk_factor"], name="unique_student_risk_factor"),
        ]

    def __str__(self):
        return f"{self.student_risk_score} - {self.risk_factor.name} ({self.contribution_weight}%)"
