"""
Migración inicial para early_alert.

Usa db_table='analytics_earlyalert' para mantener compatibilidad
con la tabla existente del app anterior 'analytics'.
"""

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("students", "0001_initial"),
        ("academic_period", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="EarlyAlert",
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
                    models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización"),
                ),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="Activo"),
                ),
                (
                    "sync_id",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="ID externo del sistema integrado",
                        max_length=100,
                        verbose_name="ID Sincronización",
                    ),
                ),
                (
                    "sync_status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("pending", "Pendiente"),
                            ("synced", "Sincronizado"),
                            ("error", "Error"),
                        ],
                        default="pending",
                        max_length=20,
                        verbose_name="Estado de Sincronización",
                    ),
                ),
                (
                    "last_sync_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Última Sincronización"
                    ),
                ),
                (
                    "alert_type",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("low_attendance", "Baja Asistencia"),
                            ("failing_grades", "Calificaciones Bajas"),
                            ("behavioral", "Problemas de Conducta"),
                            ("dropout_risk", "Riesgo de Deserción"),
                            ("socioemotional", "Problemas Socioemocionales"),
                        ],
                        max_length=30,
                        null=True,
                        verbose_name="Tipo de alerta",
                    ),
                ),
                ("description", models.TextField(verbose_name="Descripción")),
                (
                    "urgency_level",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("low", "Baja"),
                            ("medium", "Media"),
                            ("high", "Alta"),
                            ("critical", "Crítica"),
                        ],
                        max_length=20,
                        null=True,
                        verbose_name="Nivel de urgencia",
                    ),
                ),
                ("attended", models.BooleanField(default=False, verbose_name="Atendida")),
                (
                    "detected_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Fecha de detección"
                    ),
                ),
                (
                    "attended_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Fecha de atención"
                    ),
                ),
                (
                    "response_actions",
                    models.TextField(
                        blank=True, default="", verbose_name="Acciones de respuesta"
                    ),
                ),
                (
                    "academic_period",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="early_alerts",
                        to="academic_period.academicperiod",
                        verbose_name="Período Académico",
                    ),
                ),
                (
                    "attended_by_user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="attended_alerts",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Atendida por",
                    ),
                ),
                (
                    "enrollment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="early_alerts",
                        to="students.enrollment",
                        verbose_name="Matrícula",
                    ),
                ),
            ],
            options={
                "verbose_name": "Alerta Temprana",
                "verbose_name_plural": "Alertas Tempranas",
                "db_table": "analytics_earlyalert",
                "ordering": ["-detected_at"],
            },
        ),
        migrations.AddIndex(
            model_name="earlyalert",
            index=models.Index(
                fields=["attended", "urgency_level"], name="analytics_e_attende_4c6fbd_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="earlyalert",
            index=models.Index(
                fields=["enrollment", "academic_period"],
                name="analytics_e_enrollm_4c6fbd_idx",
            ),
        ),
    ]
