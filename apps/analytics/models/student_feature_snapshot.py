from django.db import models
from apps.core.models import TimeStampedModel


class StudentFeatureSnapshot(TimeStampedModel):
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        verbose_name="Matrícula",
        help_text="Matrícula del estudiante",
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
    # ─── Dimensiones analíticas / de segmentación (Fase 4 · Auditoría §5 F) ───
    # NO son features numéricas del modelo ML (ciudad = alta cardinalidad,
    # motivo de retiro = variable de resultado / fuga de información). Se persisten
    # para segmentar riesgo y deserción en dashboards y reportes.
    city = models.ForeignKey(
        "people.City",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="feature_snapshots",
        verbose_name="Ciudad de Origen",
    )
    special_needs_type = models.ForeignKey(
        "students.SpecialNeedsType",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="feature_snapshots",
        verbose_name="Tipo de NEE",
    )
    withdrawal_reason = models.ForeignKey(
        "students.WithdrawalReason",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="feature_snapshots",
        verbose_name="Motivo de Retiro",
    )
    is_current = models.BooleanField(default=False, verbose_name="Es actual")
    snapshot_trigger = models.CharField(
        max_length=10,
        choices=[("MANUAL", "Manual"), ("AUTO", "Automático"), ("BATCH", "Por Lote")],
        default="MANUAL",
        verbose_name="Desencadenante",
    )
    calculated_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Cálculo")

    class Meta:
        app_label = "analytics"
        verbose_name = "Instantánea de Métricas de Estudiante"
        verbose_name_plural = "Instantáneas de Métricas de Estudiantes"
        unique_together = ["enrollment", "academic_period"]
        indexes = [
            models.Index(fields=["academic_period", "failing_subjects_count"]),
            models.Index(fields=["academic_period", "attendance_rate"]),
            models.Index(fields=["calculated_at"]),
            models.Index(fields=["enrollment", "academic_period", "is_current"]),
        ]

    def __str__(self):
        return f"Features for {self.enrollment} ({self.academic_period})"

    def save(self, *args, **kwargs):
        if self.is_current:
            StudentFeatureSnapshot.objects.filter(
                enrollment=self.enrollment,
                academic_period=self.academic_period,
                is_current=True,
            ).exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)