from django.apps import AppConfig


class StudentNoteConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.grading.student_note"
    label = "grading_student_note"
    verbose_name = "Calificaciones"

    def ready(self):
        import apps.grading.student_note.signals  # noqa: F401
