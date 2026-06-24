from django.contrib import admin

from .infrastructure.models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("id", "enrollment", "teacher_subject_section", "academic_period", "attendance_status", "attendance_date", "absence_type")
    list_filter = ("attendance_status", "absence_type", "attendance_date", "academic_period")
    search_fields = ("enrollment__student__user__person__names", "observation")
