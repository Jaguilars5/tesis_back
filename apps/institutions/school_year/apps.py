from django.apps import AppConfig


class SchoolYearConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.institutions.school_year"
    label = "institutions_school_year"
    verbose_name = "A\u00f1os Escolares"

    def ready(self):
        import apps.institutions.school_year.signals  # noqa: F401
