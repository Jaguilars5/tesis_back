from django.apps import AppConfig


class SubjectAcademicConfigConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.academic.subject_academic_config"
    label = "academic_subject_config"
    verbose_name = "Configuraciones de Materia por Grado"

    def ready(self):
        import apps.academic.subject_academic_config.signals  # noqa: F401
