from django.apps import AppConfig


class IncidentTypeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.behavior.incident_type"
    label = "behavior_incident_type"
    verbose_name = "Tipos de Incidente"

    def ready(self):
        import apps.behavior.incident_type.signals  # noqa: F401
