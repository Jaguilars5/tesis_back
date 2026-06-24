from django.apps import AppConfig


class SeverityConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.behavior.severity"
    label = "behavior_severity"
    verbose_name = "Severidades"

    def ready(self):
        import apps.behavior.severity.signals  # noqa: F401
