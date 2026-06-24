from django.apps import AppConfig


class AttendanceStatusConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.attendance.attendance_status"
    label = "attendance_attendance_status"
    verbose_name = "Estados de Asistencia"

    def ready(self):
        import apps.attendance.attendance_status.signals  # noqa: F401
