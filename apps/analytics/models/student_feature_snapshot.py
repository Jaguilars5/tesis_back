from django.db import models
from apps.core.models import TimeStampedModel


class StudentFeatureSnapshot(TimeStampedModel):
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        verbose_name="Matrícula",
        help_text="Matrícula del estudiante",
        null=True,  # Permite null temporal para facilitar migraciones desde el modelo antiguo
    )
    academic_period = models.ForeignKey(
        "academic.AcademicPeriod",
        on_delete=models.CASCADE,
        verbose_name="Período Académico",
    )
    attendance_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00, verbose_name="Tasa de Asistencia"
    )
    consecutive_absences_max = models.IntegerField(
        default=0, verbose_name="Máximo de Faltas Consecutivas"
    )
    tardiness_count = models.IntegerField(default=0, verbose_name="Contador de Atrasos")
    justified_absences = models.IntegerField(
        default=0, verbose_name="Ausencias Justificadas"
    )
    unjustified_absences = models.IntegerField(
        default=0, verbose_name="Ausencias Injustificadas"
    )
    formative_avg_normalized = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00, verbose_name="Promedio Formativo Normalizado"
    )
    summative_avg_normalized = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00, verbose_name="Promedio Sumativo Normalizado"
    )
    grade_trend_slope = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00, verbose_name="Tendencia de Notas"
    )
    failing_subjects_count = models.IntegerField(
        default=0, verbose_name="Materias Reprobadas"
    )
    conduct_score = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00, verbose_name="Puntaje de Conducta"
    )
    severe_incidents_count = models.IntegerField(
        default=0, verbose_name="Incidentes Graves"
    )
    family_notified_ratio = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00, verbose_name="Ratio de Notificación Familiar"
    )
    prev_period_avg_grade = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name="Promedio Período Anterior",
    )
    age_grade_gap = models.IntegerField(default=0, verbose_name="Brecha Edad-Grado")
    is_repeat = models.BooleanField(default=False, verbose_name="Es Repitente")
    has_special_needs = models.BooleanField(
        default=False, verbose_name="Tiene NEE"
    )
    residential_zone = models.CharField(
        max_length=50, blank=True, verbose_name="Zona de Residencia"
    )
    distance_to_school_km = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name="Distancia al Colegio (km)",
    )
    active_alerts = models.IntegerField(default=0, verbose_name="Alertas Activas")
    calculated_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Cálculo")

    class Meta:
        app_label = "analytics"
        verbose_name = "Instantánea de Métricas de Estudiante"
        verbose_name_plural = "Instantáneas de Métricas de Estudiantes"

    def __str__(self):
        return f"Features for {self.enrollment} ({self.academic_period})"
