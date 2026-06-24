from django.apps import AppConfig


class SubjectConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.academic.subject"
    label = "academic_subject"
    verbose_name = "Materias"

    def ready(self):
        import apps.academic.subject.signals  # noqa: F401
