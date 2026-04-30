from django.db import models

class StudentRiskScore(models.Model):
    """
    Puntuación de riesgo académico calculada para un estudiante.

    student: Estudiante evaluado
    academic_period: Período académico del cálculo
    risk_score: Valor numérico del riesgo (0 a 1 o 0 a 100)
    risk_label: Etiqueta categórica (Bajo, Medio, Alto)
    top_factors: JSON con los factores que más influyeron en el riesgo
    model_version: Versión del modelo predictivo utilizado
    calculated_at: Fecha y hora del cálculo
    """

    student = models.ForeignKey(
        "students.Student", on_delete=models.CASCADE, help_text="Estudiante evaluado"
    )
    academic_period = models.ForeignKey(
        "academic.Academic_Period",
        on_delete=models.CASCADE,
        help_text="Período académico correspondiente",
    )
    risk_score = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Puntaje de riesgo calculado"
    )
    risk_label = models.CharField(
        max_length=20, help_text="Etiqueta de nivel de riesgo (Bajo, Medio, Alto)"
    )
    top_factors = models.JSONField(
        help_text="Factores principales que contribuyen al riesgo"
    )
    model_version = models.CharField(
        max_length=50, help_text="Versión del modelo de IA/Analítica"
    )
    calculated_at = models.DateTimeField(
        auto_now_add=True, help_text="Fecha de cálculo del puntaje"
    )

    class Meta:
        app_label = "analytics"
        ordering = ["-calculated_at"]

    def __str__(self):
        return f"{self.student} - {self.risk_label} ({self.risk_score})"
