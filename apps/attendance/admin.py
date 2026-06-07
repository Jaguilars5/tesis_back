from django.contrib import admin
from .models import (
    Attendance, AttendanceStatus, IncidentType, ConductIncident,
    SocioemotionalSkill, SkillEvaluation, BehaviorEvaluation,
)


@admin.register(AttendanceStatus)
class AttendanceStatusAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    search_fields = ("code", "name")


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("id", "enrollment", "teacher_subject_section", "academic_period", "attendance_status", "attendance_date", "absence_type")
    list_filter = ("attendance_status", "absence_type", "attendance_date", "academic_period")
    search_fields = ("enrollment__student__person__names", "observation")


@admin.register(IncidentType)
class IncidentTypeAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "description")
    search_fields = ("code", "name")


@admin.register(ConductIncident)
class ConductIncidentAdmin(admin.ModelAdmin):
    list_display = ("id", "enrollment", "reported_by_user", "academic_period", "incident_type", "incident_date", "severity")
    list_filter = ("severity", "incident_date", "academic_period", "incident_type")
    search_fields = ("enrollment__student__person__names", "description", "actions_taken")


@admin.register(SocioemotionalSkill)
class SocioemotionalSkillAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "active")
    list_filter = ("active",)
    search_fields = ("code", "name")


@admin.register(SkillEvaluation)
class SkillEvaluationAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "academic_period", "socioemotional_skill", "qualitative_scale", "evaluation_date")
    list_filter = ("academic_period", "socioemotional_skill", "qualitative_scale")
    search_fields = ("enrollment__student__person__names", "observation")


@admin.register(BehaviorEvaluation)
class BehaviorEvaluationAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "academic_period", "calculated_scale", "final_scale")
    list_filter = ("academic_period", "calculated_scale", "final_scale")
    search_fields = ("enrollment__student__person__names",)
