from django.apps import AppConfig


class AcademicLevelConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.institutions.academic_level"
    label = "institutions_academic_level"
    verbose_name = "Niveles Acad\u00e9micos"

    def ready(self):
        import apps.institutions.academic_level.signals  # noqa: F401
