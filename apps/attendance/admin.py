from django.contrib import admin
from .models import AbsenceType, Attendance, AttendanceStatus


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("id", "enrollment", "teacher_subject_section", "academic_period", "attendance_status", "attendance_date", "absence_type")
    list_filter = ("attendance_status", "absence_type", "attendance_date", "academic_period")
    search_fields = ("enrollment__student__person__names", "observation")


@admin.register(AttendanceStatus)
class AttendanceStatusAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active", "tipo")
    list_filter = ("is_active", "tipo")
    search_fields = ("code", "name")


@admin.register(AbsenceType)
class AbsenceTypeAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("code", "name")
