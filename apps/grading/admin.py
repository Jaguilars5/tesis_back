"""
Configuración del panel administrativo para el módulo Grading.
"""

from django.contrib import admin

from .models import Attendance, ConductIncident, StudentNote


@admin.register(StudentNote)
class StudentNoteAdmin(admin.ModelAdmin):
    """
    Administración de calificaciones de estudiantes.
    """

    list_display = (
        "id",
        "student",
        "academic_activity",
        "academic_period",
        "teacher_subject_section",
        "note_value",
        "normalized_value",
        "active",
        "created_at",
    )
    list_filter = ("active", "academic_period", "sync_status")
    search_fields = (
        "student__names",
        "student__last_names",
        "academic_activity__name",
    )


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    """
    Administración de registros de asistencia.
    """

    list_display = (
        "id",
        "student",
        "teacher_subject_section",
        "academic_period",
        "date",
        "status",
        "created_at",
    )
    list_filter = ("status", "academic_period", "date")
    search_fields = ("student__names", "student__last_names")


@admin.register(ConductIncident)
class ConductIncidentAdmin(admin.ModelAdmin):
    """
    Administración de incidentes de conducta.
    """

    list_display = (
        "id",
        "student",
        "reported_by",
        "academic_period",
        "incident_date",
        "category",
        "severity",
        "family_notified",
        "created_at",
    )
    list_filter = ("category", "severity", "family_notified", "academic_period")
    search_fields = ("student__names", "student__last_names", "description")

