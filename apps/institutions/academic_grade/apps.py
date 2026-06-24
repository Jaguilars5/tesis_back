from django.apps import AppConfig


class InstitutionsAcademicGradeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.institutions.academic_grade"
    label = "institutions_academic_grade"
    verbose_name = "Grados Académicos"

    def ready(self):
        import apps.institutions.academic_grade.signals  # noqa: F401
