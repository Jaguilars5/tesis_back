from django.db import models

class StudentFeatureSnapshot(models.Model):
    """
    Instantánea de métricas (features) de un estudiante para un periodo.
    Sirve como entrada para los modelos de predicción de riesgo.

    attendance_rate: Tasa de asistencia (0.0 a 1.0)
    consecutive_absences_max: Máximo de faltas consecutivas
    tardiness_count: Cantidad de atrasos
    avg_grade_normalized: Promedio de notas normalizado (base 10)
    grade_trend_slope: Pendiente de la tendencia de notas (mejora o empeora)
    failing_subjects_count: Cantidad de materias con nota insuficiente
    conduct_score: Puntaje de conducta calculado
    family_notified_ratio: Proporción de incidentes notificados a la familia
    prev_period_avg_grade: Promedio del periodo anterior
    age_grade_gap: Brecha de edad respecto al grado correspondiente
    """

    student = models.ForeignKey(
        "students.Student", on_delete=models.CASCADE, help_text="Estudiante"
    )
    academic_period = models.ForeignKey(
        "academic.Academic_Period",
        on_delete=models.CASCADE,
        help_text="Período académico",
    )
    attendance_rate = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Porcentaje de asistencia"
    )
    consecutive_absences_max = models.IntegerField(help_text="Máximo de faltas seguidas")
    tardiness_count = models.IntegerField(help_text="Total de atrasos")
    avg_grade_normalized = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Promedio general normalizado"
    )
    grade_trend_slope = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Tendencia de rendimiento"
    )
    failing_subjects_count = models.IntegerField(help_text="Materias con pérdida")
    conduct_score = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Puntaje de comportamiento"
    )
    family_notified_ratio = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Ratio de notificación familiar"
    )
    prev_period_avg_grade = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Promedio periodo anterior",
    )
    age_grade_gap = models.IntegerField(help_text="Desfase edad-grado")
    calculated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "analytics"

    def __str__(self):
        return f"Features for {self.student} ({self.academic_period})"
