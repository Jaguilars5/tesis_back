from django.apps import AppConfig


class ConductIncidentConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.behavior.conduct_incident"
    label = "behavior_conduct_incident"
    verbose_name = "Incidentes de Conducta"

    def ready(self):
        import apps.behavior.conduct_incident.signals  # noqa: F401
