from django.apps import AppConfig


class SectionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.institutions.section"
    label = "institutions_section"
    verbose_name = "Secciones"

    def ready(self):
        import apps.institutions.section.signals  # noqa: F401
