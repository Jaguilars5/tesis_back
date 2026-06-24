from django.apps import AppConfig


class IamConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.iam"
    verbose_name = "Identidad y Acceso"

    def ready(self):
        import apps.iam.signals  # noqa: F401
