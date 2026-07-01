from django.apps import AppConfig


class IntegrationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.integration"

    def ready(self):
        from .tasks.sync_tasks import load_sync_handlers

        load_sync_handlers()
