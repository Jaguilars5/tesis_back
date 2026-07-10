"""
Modelos Django para riesgo estudiantil.

Mantiene las tablas originales mediante db_table explícito
para compatibilidad con migraciones existentes.
"""

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


# ─────────────────────────────────────────────────────────────────────────────
# RiskFactor (catálogo)
# ─────────────────────────────────────────────────────────────────────────────

class RiskFactor(TimeStampedModel):
    """Factor de riesgo catalogado (LOW_ATTENDANCE, FAILING_GRADES, etc.)."""

    code = models.CharField(max_length=30, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, default="", verbose_name="Descripción")

    class Meta:
        app_label = "student_risk"
        db_table = "analytics_riskfactor"  # Preservar tabla existente
        verbose_name = "Factor de Riesgo"
        verbose_name_plural = "Factores de Riesgo"
        ordering = ["name"]

    def __str__(self):
        return self.name


# ─────────────────────────────────────────────────────────────────────────────
# StudentRiskScore
# ─────────────────────────────────────────────────────────────────────────────

class StudentRiskScore(TimeStampedModel):
    """Puntaje de riesgo calculado para un estudiante en un período."""

    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        verbose_name="Matrícula",
    )
    academic_period = models.ForeignKey(
        "academic_period.AcademicPeriod",
        on_delete=models.CASCADE,
        verbose_name="Período Académico",
    )
    risk_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name="Puntaje de Riesgo",
    )
    risk_label = models.CharField(
        max_length=20,
        default="",
        verbose_name="Etiqueta de Riesgo",
    )
    model_version = models.CharField(
        max_length=50,
        default="",
        verbose_name="Versión del Modelo",
    )
    calculated_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Cálculo",
    )

    class Meta:
        app_label = "student_risk"
        db_table = "analytics_studentriskscore"  # Preservar tabla existente
        verbose_name = "Puntaje de Riesgo del Estudiante"
        verbose_name_plural = "Puntajes de Riesgo de los Estudiantes"
        ordering = ["-calculated_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["enrollment", "academic_period", "model_version"],
                name="student_risk_unique_enrollment_period_model",
            ),
        ]
        indexes = [
            models.Index(fields=["academic_period", "risk_label"]),
            models.Index(fields=["calculated_at"]),
        ]

    def __str__(self):
        return f"{self.enrollment} - {self.risk_label} ({self.risk_score})"


# ─────────────────────────────────────────────────────────────────────────────
# StudentRiskFactor
# ─────────────────────────────────────────────────────────────────────────────

class StudentRiskFactor(TimeStampedModel):
    """Relación entre un puntaje de riesgo y los factores que contribuyen."""

    student_risk_score = models.ForeignKey(
        StudentRiskScore,
        on_delete=models.CASCADE,
        related_name="risk_factors",
        verbose_name="Puntaje de Riesgo",
    )
    risk_factor = models.ForeignKey(
        RiskFactor,
        on_delete=models.CASCADE,
        verbose_name="Factor de Riesgo",
    )
    contribution_weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Peso de Contribución (%)",
    )

    class Meta:
        app_label = "student_risk"
        db_table = "analytics_studentriskfactor"  # Preservar tabla existente
        verbose_name = "Factor de Riesgo del Estudiante"
        verbose_name_plural = "Factores de Riesgo de los Estudiantes"
        constraints = [
            models.UniqueConstraint(
                fields=["student_risk_score", "risk_factor"],
                name="student_risk_unique_score_factor",
            ),
        ]

    def __str__(self):
        return f"{self.student_risk_score} - {self.risk_factor.name} ({self.contribution_weight}%)"


# ─────────────────────────────────────────────────────────────────────────────
# StudentFeatureSnapshot
# ─────────────────────────────────────────────────────────────────────────────

class StudentFeatureSnapshot(TimeStampedModel):
    """Snapshot de features calculadas para análisis de riesgo."""

    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        verbose_name="Matrícula",
        help_text="Matrícula del estudiante",
    )
    academic_period = models.ForeignKey(
        "academic_period.AcademicPeriod",
        on_delete=models.CASCADE,
        verbose_name="Período Académico",
    )
    # Features de asistencia
    attendance_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name="Tasa de Asistencia",
    )
    consecutive_absences_max = models.IntegerField(
        default=0,
        verbose_name="Máximo de Faltas Consecutivas",
    )
    tardiness_count = models.IntegerField(
        default=0,
        verbose_name="Contador de Atrasos",
    )
    justified_absences = models.IntegerField(
        default=0,
        verbose_name="Ausencias Justificadas",
    )
    unjustified_absences = models.IntegerField(
        default=0,
        verbose_name="Ausencias Injustificadas",
    )
    # Features académicas
    formative_avg_normalized = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name="Promedio Formativo Normalizado",
    )
    summative_avg_normalized = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name="Promedio Sumativo Normalizado",
    )
    grade_trend_slope = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name="Tendencia de Notas",
    )
    failing_subjects_count = models.IntegerField(
        default=0,
        verbose_name="Materias Reprobadas",
    )
    # Features de conducta
    conduct_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name="Puntaje de Conducta",
    )
    severe_incidents_count = models.IntegerField(
        default=0,
        verbose_name="Incidentes Graves",
    )
    family_notified_ratio = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name="Ratio de Notificación Familiar",
    )
    # Features históricas y demográficas
    prev_period_avg_grade = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Promedio Período Anterior",
    )
    age_grade_gap = models.IntegerField(
        default=0,
        verbose_name="Brecha Edad-Grado",
    )
    is_repeat = models.BooleanField(
        default=False,
        verbose_name="Es Repitente",
    )
    has_special_needs = models.BooleanField(
        default=False,
        verbose_name="Tiene NEE",
    )
    # Dimensiones analíticas (Fase 4)
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
    # Metadata
    is_current = models.BooleanField(
        default=False,
        verbose_name="Es actual",
    )
    snapshot_trigger = models.CharField(
        max_length=10,
        choices=[
            ("MANUAL", "Manual"),
            ("AUTO", "Automático"),
            ("BATCH", "Por Lote"),
        ],
        default="MANUAL",
        verbose_name="Desencadenante",
    )
    calculated_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Cálculo",
    )

    class Meta:
        app_label = "student_risk"
        db_table = "analytics_studentfeaturesnapshot"  # Preservar tabla existente
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
        """Asegura unicidad de is_current por (enrollment, academic_period)."""
        if self.is_current:
            StudentFeatureSnapshot.objects.filter(
                enrollment=self.enrollment,
                academic_period=self.academic_period,
                is_current=True,
            ).exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)


# ─────────────────────────────────────────────────────────────────────────────
# RiskScoringConfig (singleton)
# ─────────────────────────────────────────────────────────────────────────────

class ScoringEngineChoices(models.TextChoices):
    """Motor activo para el cálculo del riesgo académico."""

    RULES = "reglas", "Motor de reglas (ponderado + umbrales)"
    ML = "ML", "Modelo de Machine Learning"


class ScoringPresetChoices(models.TextChoices):
    """Presets cerrados como punto de partida seguro."""

    CONSERVADOR = "conservador", "Conservador"
    EQUILIBRADO = "equilibrado", "Equilibrado"
    ESTRICTO = "estricto", "Estricto"
    PERSONALIZADO = "personalizado", "Personalizado"


class RiskScoringConfig(TimeStampedModel):
    """
    Configuración GLOBAL (singleton) del motor de riesgo académico.

    Externaliza pesos y umbrales que históricamente vivían hardcodeados.
    Es un singleton: existe a lo sumo una fila (pk fijo = 1).
    """

    SINGLETON_PK = 1

    engine = models.CharField(
        max_length=10,
        choices=ScoringEngineChoices.choices,
        default=ScoringEngineChoices.RULES,
        verbose_name="Motor de cálculo",
    )
    preset = models.CharField(
        max_length=15,
        choices=ScoringPresetChoices.choices,
        default=ScoringPresetChoices.EQUILIBRADO,
        verbose_name="Preset aplicado",
    )

    # Pesos de dimensión (porcentajes, deben sumar 100)
    weight_conducta = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=30.00,
        verbose_name="Peso Conducta (%)",
    )
    weight_asistencia = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=35.00,
        verbose_name="Peso Asistencia (%)",
    )
    weight_calificaciones = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=35.00,
        verbose_name="Peso Calificaciones (%)",
    )

    # Umbrales del semáforo de asistencia (0–100)
    attendance_red_max = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=70.00,
        verbose_name="Asistencia máxima para Rojo (%)",
    )
    attendance_yellow_max = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=85.00,
        verbose_name="Asistencia máxima para Amarillo (%)",
    )

    # Umbrales del semáforo de promedio (0–10)
    average_red_max = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=6.00,
        verbose_name="Promedio máximo para Rojo",
    )
    average_yellow_max = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=7.00,
        verbose_name="Promedio máximo para Amarillo",
    )
    attendance_green_min = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=85.01,
        verbose_name="Asistencia mínima para Verde (%)",
    )
    average_green_min = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=7.01,
        verbose_name="Promedio mínimo para Verde",
    )

    # Umbrales de conducta (conteos)
    severe_red_min = models.IntegerField(
        default=3,
        verbose_name="Faltas graves para Rojo (>)",
    )
    mild_yellow_min = models.IntegerField(
        default=5,
        verbose_name="Faltas leves para Amarillo (>)",
    )
    severe_green_max = models.IntegerField(
        default=0,
        verbose_name="Faltas graves máximas para Verde (≤)",
    )
    mild_green_max = models.IntegerField(
        default=5,
        verbose_name="Faltas leves máximas para Verde (≤)",
    )

    # Umbrales del puntaje final (0–100) para el semáforo de riesgo
    score_red_min = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=70.00,
        verbose_name="Puntaje mínimo para Rojo (≥)",
        help_text="Los puntajes >= este valor se clasifican como Rojo",
    )
    score_yellow_min = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=40.00,
        verbose_name="Puntaje mínimo para Amarillo (≥)",
        help_text="Los puntajes >= este valor y < score_red_min se clasifican como Amarillo",
    )

    class Meta:
        app_label = "student_risk"
        db_table = "analytics_riskscoringconfig"  # Preservar tabla existente
        verbose_name = "Configuración de Cálculo de Riesgo"
        verbose_name_plural = "Configuración de Cálculo de Riesgo"

    def __str__(self):
        return f"RiskScoringConfig(engine={self.engine}, preset={self.preset})"
