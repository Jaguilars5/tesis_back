from django.apps import AppConfig


class StudentRiskConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.analytics.student_risk"
    label = "student_risk"
    verbose_name = "Riesgo Estudiantil"

    def ready(self):
        import apps.analytics.student_risk.signals  # noqa: F401
