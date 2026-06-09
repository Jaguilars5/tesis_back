from django.contrib import admin
from .models import (
    IncidentType, SocioemotionalSkill, ConductIncident,
    SkillEvaluation, BehaviorEvaluation, DiagnosticEvaluation,
)


@admin.register(IncidentType)
class IncidentTypeAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "is_active"]
    list_filter = ["is_active"]


@admin.register(SocioemotionalSkill)
class SocioemotionalSkillAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "is_active"]
    list_filter = ["is_active"]


@admin.register(ConductIncident)
class ConductIncidentAdmin(admin.ModelAdmin):
    list_display = ["id", "enrollment", "reported_by_user", "academic_period", "incident_type", "incident_date", "severity"]
    list_filter = ["severity", "incident_date"]
    search_fields = ["enrollment__student__person__names", "description"]


@admin.register(SkillEvaluation)
class SkillEvaluationAdmin(admin.ModelAdmin):
    list_display = ["enrollment", "academic_period", "socioemotional_skill", "qualitative_scale"]
    list_filter = ["academic_period", "socioemotional_skill"]


@admin.register(BehaviorEvaluation)
class BehaviorEvaluationAdmin(admin.ModelAdmin):
    list_display = ["enrollment", "academic_period", "calculated_scale", "final_scale"]
    list_filter = ["academic_period"]


@admin.register(DiagnosticEvaluation)
class DiagnosticEvaluationAdmin(admin.ModelAdmin):
    list_display = ["enrollment", "academic_period", "socioemotional_area", "application_date"]
    list_filter = ["academic_period"]
