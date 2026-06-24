"""
Migración inicial para student_risk.

Usa db_table explícito para cada modelo para mantener compatibilidad
con las tablas existentes del app anterior 'analytics'.
"""

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("academic_period", "0001_initial"),
        ("people", "0001_initial"),
        ("students", "0001_initial"),
    ]

    operations = [
        # RiskFactor
        migrations.CreateModel(
            name="RiskFactor",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Fecha de Creación"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Fecha de Actualización"
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="Activo"),
                ),
                (
                    "code",
                    models.CharField(
                        max_length=30, unique=True, verbose_name="Código"
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=100, verbose_name="Nombre"),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True, default="", verbose_name="Descripción"
                    ),
                ),
            ],
            options={
                "verbose_name": "Factor de Riesgo",
                "verbose_name_plural": "Factores de Riesgo",
                "db_table": "analytics_riskfactor",
                "ordering": ["name"],
            },
        ),
        # StudentRiskScore
        migrations.CreateModel(
            name="StudentRiskScore",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Fecha de Creación"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Fecha de Actualización"
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="Activo"),
                ),
                (
                    "risk_score",
                    models.DecimalField(
                        decimal_places=2,
                        default=0.0,
                        max_digits=5,
                        verbose_name="Puntaje de Riesgo",
                    ),
                ),
                (
                    "risk_label",
                    models.CharField(
                        default="", max_length=20, verbose_name="Etiqueta de Riesgo"
                    ),
                ),
                (
                    "model_version",
                    models.CharField(
                        default="",
                        max_length=50,
                        verbose_name="Versión del Modelo",
                    ),
                ),
                (
                    "calculated_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Fecha de Cálculo"
                    ),
                ),
                (
                    "academic_period",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="academic_period.academicperiod",
                        verbose_name="Período Académico",
                    ),
                ),
                (
                    "enrollment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="students.enrollment",
                        verbose_name="Matrícula",
                    ),
                ),
            ],
            options={
                "verbose_name": "Puntaje de Riesgo del Estudiante",
                "verbose_name_plural": "Puntajes de Riesgo de los Estudiantes",
                "db_table": "analytics_studentriskscore",
                "ordering": ["-calculated_at"],
            },
        ),
        migrations.AddIndex(
            model_name="studentriskscore",
            index=models.Index(
                fields=["academic_period", "risk_label"],
                name="analytics_s_period_9a4fbd_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="studentriskscore",
            index=models.Index(
                fields=["calculated_at"],
                name="analytics_s_calcu_9a4fbd_idx",
            ),
        ),
        migrations.AddConstraint(
            model_name="studentriskscore",
            constraint=models.UniqueConstraint(
                fields=["enrollment", "academic_period", "model_version"],
                name="student_risk_unique_enrollment_period_model",
            ),
        ),
        # StudentRiskFactor
        migrations.CreateModel(
            name="StudentRiskFactor",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Fecha de Creación"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Fecha de Actualización"
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="Activo"),
                ),
                (
                    "contribution_weight",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=5,
                        verbose_name="Peso de Contribución (%)",
                    ),
                ),
                (
                    "risk_factor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="student_risk.riskfactor",
                        verbose_name="Factor de Riesgo",
                    ),
                ),
                (
                    "student_risk_score",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="risk_factors",
                        to="student_risk.studentriskscore",
                        verbose_name="Puntaje de Riesgo",
                    ),
                ),
            ],
            options={
                "verbose_name": "Factor de Riesgo del Estudiante",
                "verbose_name_plural": "Factores de Riesgo de los Estudiantes",
                "db_table": "analytics_studentriskfactor",
            },
        ),
        migrations.AddConstraint(
            model_name="studentriskfactor",
            constraint=models.UniqueConstraint(
                fields=["student_risk_score", "risk_factor"],
                name="student_risk_unique_score_factor",
            ),
        ),
        # StudentFeatureSnapshot
        migrations.CreateModel(
            name="StudentFeatureSnapshot",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Fecha de Creación"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Fecha de Actualización"
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="Activo"),
                ),
                (
                    "attendance_rate",
                    models.DecimalField(
                        decimal_places=2,
                        default=0.0,
                        max_digits=5,
                        verbose_name="Tasa de Asistencia",
                    ),
                ),
                (
                    "consecutive_absences_max",
                    models.IntegerField(
                        default=0, verbose_name="Máximo de Faltas Consecutivas"
                    ),
                ),
                (
                    "tardiness_count",
                    models.IntegerField(
                        default=0, verbose_name="Contador de Atrasos"
                    ),
                ),
                (
                    "justified_absences",
                    models.IntegerField(
                        default=0, verbose_name="Ausencias Justificadas"
                    ),
                ),
                (
                    "unjustified_absences",
                    models.IntegerField(
                        default=0, verbose_name="Ausencias Injustificadas"
                    ),
                ),
                (
                    "formative_avg_normalized",
                    models.DecimalField(
                        decimal_places=2,
                        default=0.0,
                        max_digits=5,
                        verbose_name="Promedio Formativo Normalizado",
                    ),
                ),
                (
                    "summative_avg_normalized",
                    models.DecimalField(
                        decimal_places=2,
                        default=0.0,
                        max_digits=5,
                        verbose_name="Promedio Sumativo Normalizado",
                    ),
                ),
                (
                    "grade_trend_slope",
                    models.DecimalField(
                        decimal_places=2,
                        default=0.0,
                        max_digits=5,
                        verbose_name="Tendencia de Notas",
                    ),
                ),
                (
                    "failing_subjects_count",
                    models.IntegerField(
                        default=0, verbose_name="Materias Reprobadas"
                    ),
                ),
                (
                    "conduct_score",
                    models.DecimalField(
                        decimal_places=2,
                        default=0.0,
                        max_digits=5,
                        verbose_name="Puntaje de Conducta",
                    ),
                ),
                (
                    "severe_incidents_count",
                    models.IntegerField(
                        default=0, verbose_name="Incidentes Graves"
                    ),
                ),
                (
                    "family_notified_ratio",
                    models.DecimalField(
                        decimal_places=2,
                        default=0.0,
                        max_digits=5,
                        verbose_name="Ratio de Notificación Familiar",
                    ),
                ),
                (
                    "prev_period_avg_grade",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=5,
                        null=True,
                        verbose_name="Promedio Período Anterior",
                    ),
                ),
                (
                    "age_grade_gap",
                    models.IntegerField(
                        default=0, verbose_name="Brecha Edad-Grado"
                    ),
                ),
                ("is_repeat", models.BooleanField(default=False, verbose_name="Es Repitente")),
                (
                    "has_special_needs",
                    models.BooleanField(
                        default=False, verbose_name="Tiene NEE"
                    ),
                ),
                (
                    "is_current",
                    models.BooleanField(default=False, verbose_name="Es actual"),
                ),
                (
                    "snapshot_trigger",
                    models.CharField(
                        choices=[
                            ("MANUAL", "Manual"),
                            ("AUTO", "Automático"),
                            ("BATCH", "Por Lote"),
                        ],
                        default="MANUAL",
                        max_length=10,
                        verbose_name="Desencadenante",
                    ),
                ),
                (
                    "calculated_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Fecha de Cálculo"
                    ),
                ),
                (
                    "academic_period",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="academic_period.academicperiod",
                        verbose_name="Período Académico",
                    ),
                ),
                (
                    "city",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="feature_snapshots",
                        to="people.city",
                        verbose_name="Ciudad de Origen",
                    ),
                ),
                (
                    "enrollment",
                    models.ForeignKey(
                        help_text="Matrícula del estudiante",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="students.enrollment",
                        verbose_name="Matrícula",
                    ),
                ),
                (
                    "special_needs_type",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="feature_snapshots",
                        to="students.specialneedstype",
                        verbose_name="Tipo de NEE",
                    ),
                ),
                (
                    "withdrawal_reason",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="feature_snapshots",
                        to="students.withdrawalreason",
                        verbose_name="Motivo de Retiro",
                    ),
                ),
            ],
            options={
                "verbose_name": "Instantánea de Métricas de Estudiante",
                "verbose_name_plural": "Instantáneas de Métricas de Estudiantes",
                "db_table": "analytics_studentfeaturesnapshot",
            },
        ),
        migrations.AddIndex(
            model_name="studentfeaturesnapshot",
            index=models.Index(
                fields=["academic_period", "failing_subjects_count"],
                name="analytics_s_period_a4fbd_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="studentfeaturesnapshot",
            index=models.Index(
                fields=["academic_period", "attendance_rate"],
                name="analytics_s_period_b4fbd_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="studentfeaturesnapshot",
            index=models.Index(
                fields=["calculated_at"],
                name="analytics_s_calcu_c4fbd_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="studentfeaturesnapshot",
            index=models.Index(
                fields=["enrollment", "academic_period", "is_current"],
                name="analytics_s_enroll_d4fbd_idx",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="studentfeaturesnapshot",
            unique_together={("enrollment", "academic_period")},
        ),
        # RiskScoringConfig
        migrations.CreateModel(
            name="RiskScoringConfig",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Fecha de Creación"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Fecha de Actualización"
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="Activo"),
                ),
                (
                    "engine",
                    models.CharField(
                        choices=[
                            ("reglas", "Motor de reglas (ponderado + umbrales)"),
                            ("ML", "Modelo de Machine Learning"),
                        ],
                        default="reglas",
                        max_length=10,
                        verbose_name="Motor de cálculo",
                    ),
                ),
                (
                    "preset",
                    models.CharField(
                        choices=[
                            ("conservador", "Conservador"),
                            ("equilibrado", "Equilibrado"),
                            ("estricto", "Estricto"),
                            ("personalizado", "Personalizado"),
                        ],
                        default="equilibrado",
                        max_length=15,
                        verbose_name="Preset aplicado",
                    ),
                ),
                (
                    "weight_conducta",
                    models.DecimalField(
                        decimal_places=2,
                        default=30.0,
                        max_digits=5,
                        verbose_name="Peso Conducta (%)",
                    ),
                ),
                (
                    "weight_asistencia",
                    models.DecimalField(
                        decimal_places=2,
                        default=35.0,
                        max_digits=5,
                        verbose_name="Peso Asistencia (%)",
                    ),
                ),
                (
                    "weight_calificaciones",
                    models.DecimalField(
                        decimal_places=2,
                        default=35.0,
                        max_digits=5,
                        verbose_name="Peso Calificaciones (%)",
                    ),
                ),
                (
                    "attendance_red_max",
                    models.DecimalField(
                        decimal_places=2,
                        default=70.0,
                        max_digits=5,
                        verbose_name="Asistencia máxima para Rojo (%)",
                    ),
                ),
                (
                    "attendance_yellow_max",
                    models.DecimalField(
                        decimal_places=2,
                        default=85.0,
                        max_digits=5,
                        verbose_name="Asistencia máxima para Amarillo (%)",
                    ),
                ),
                (
                    "average_red_max",
                    models.DecimalField(
                        decimal_places=2,
                        default=6.0,
                        max_digits=4,
                        verbose_name="Promedio máximo para Rojo",
                    ),
                ),
                (
                    "average_yellow_max",
                    models.DecimalField(
                        decimal_places=2,
                        default=7.0,
                        max_digits=4,
                        verbose_name="Promedio máximo para Amarillo",
                    ),
                ),
                (
                    "severe_red_min",
                    models.IntegerField(
                        default=3, verbose_name="Faltas graves para Rojo (>)",
                    ),
                ),
                (
                    "mild_yellow_min",
                    models.IntegerField(
                        default=5, verbose_name="Faltas leves para Amarillo (>)",
                    ),
                ),
            ],
            options={
                "verbose_name": "Configuración de Cálculo de Riesgo",
                "verbose_name_plural": "Configuración de Cálculo de Riesgo",
                "db_table": "analytics_riskscoringconfig",
            },
        ),
    ]
