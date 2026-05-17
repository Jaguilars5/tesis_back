from django.db import models


class StudentRiskScore(models.Model):
    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        verbose_name="Estudiante",
    )
    academic_period = models.ForeignKey(
        "academic.Academic_Period",
        on_delete=models.CASCADE,
        verbose_name="Período Académico",
    )
    risk_score = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Puntaje de Riesgo",
    )
    risk_label = models.CharField(
        max_length=20, verbose_name="Etiqueta de Riesgo",
    )
    model_version = models.CharField(
        max_length=50, verbose_name="Versión del Modelo",
    )
    calculated_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Cálculo",
    )

    class Meta:
        app_label = "analytics"
        ordering = ["-calculated_at"]
        verbose_name = "Puntaje de Riesgo del Estudiante"
        verbose_name_plural = "Puntajes de Riesgo de los Estudiantes"

    def __str__(self):
        return f"{self.student} - {self.risk_label} ({self.risk_score})"
