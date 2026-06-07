from django.db import models


class EarlyAlert(models.Model):
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        related_name="early_alerts",
        verbose_name="Matrícula",
    )
    academic_period = models.ForeignKey(
        "academic.Academic_Period",
        on_delete=models.CASCADE,
        related_name="early_alerts",
        verbose_name="Período Académico",
    )
    alert_type = models.CharField(
        max_length=50,
        choices=[
            ("low_attendance", "Baja Asistencia"),
            ("failing_grades", "Calificaciones Bajas"),
            ("behavioral", "Problemas de Conducta"),
            ("dropout_risk", "Riesgo de Deserción"),
            ("socioemotional", "Problemas Socioemocionales"),
        ],
        verbose_name="Tipo de alerta",
    )
    description = models.TextField(verbose_name="Descripción")
    urgency_level = models.CharField(
        max_length=20,
        choices=[
            ("low", "Baja"),
            ("medium", "Media"),
            ("high", "Alta"),
            ("critical", "Crítica"),
        ],
        verbose_name="Nivel de urgencia",
    )
    attended = models.BooleanField(default=False, verbose_name="Atendida")
    attended_by_user = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="attended_alerts",
        verbose_name="Atendida por",
    )
    detected_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de detección")
    attended_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de atención")
    response_actions = models.TextField(null=True, blank=True, verbose_name="Acciones de respuesta")

    class Meta:
        app_label = "analytics"
        verbose_name = "Alerta Temprana"
        verbose_name_plural = "Alertas Tempranas"
        ordering = ["-detected_at"]
        indexes = [
            models.Index(fields=["attended", "urgency_level"]),
            models.Index(fields=["enrollment", "academic_period"]),
        ]

    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.enrollment} ({self.get_urgency_level_display()})"
