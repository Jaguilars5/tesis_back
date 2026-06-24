from django.apps import AppConfig


class ClassScheduleConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.academic.class_schedule"
    label = "academic_class_schedule"
    verbose_name = "Horarios Académicos"

    def ready(self):
        import apps.academic.class_schedule.signals  # noqa: F401
