from django.apps import AppConfig


class PeriodTypeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.academic.period_type"
    label = "academic_period_type"
    verbose_name = "Tipos de Período"

    def ready(self):
        import apps.academic.period_type.signals  # noqa: F401
