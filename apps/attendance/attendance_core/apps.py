from django.apps import AppConfig


class AttendanceCoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.attendance.attendance_core"
    label = "attendance_core"
    verbose_name = "Registros de Asistencia"

    def ready(self):
        import apps.attendance.attendance_core.signals  # noqa: F401
