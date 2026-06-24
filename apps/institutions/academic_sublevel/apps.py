from django.apps import AppConfig


class AcademicSublevelConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.institutions.academic_sublevel"
    label = "institutions_academic_sublevel"
    verbose_name = "Subniveles Acad\u00e9micos"

    def ready(self):
        import apps.institutions.academic_sublevel.signals  # noqa: F401
