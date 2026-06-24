from django.apps import AppConfig


class AcademicPeriodConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.academic.academic_period"
    label = "academic_period"
    verbose_name = "Períodos Académicos"

    def ready(self):
        import apps.academic.academic_period.signals  # noqa: F401
