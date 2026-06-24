from django.apps import AppConfig


class ActivityTypeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.grading.activity_type"
    label = "grading_activity_type"
    verbose_name = "Tipos de Actividad"

    def ready(self):
        import apps.grading.activity_type.signals  # noqa: F401
