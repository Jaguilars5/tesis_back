from django.apps import AppConfig


class AbsenceTypeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.attendance.absence_type"
    label = "attendance_absence_type"
    verbose_name = "Tipos de Ausencia"

    def ready(self):
        import apps.attendance.absence_type.signals  # noqa: F401
