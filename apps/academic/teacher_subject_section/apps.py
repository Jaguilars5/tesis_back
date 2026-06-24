from django.apps import AppConfig


class TeacherSubjectSectionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.academic.teacher_subject_section"
    label = "academic_teacher_subject"
    verbose_name = "Docentes-Materias-Secciones"

    def ready(self):
        import apps.academic.teacher_subject_section.signals  # noqa: F401
