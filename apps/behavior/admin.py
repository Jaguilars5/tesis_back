from django.contrib import admin
from .models import (
    IncidentType, ConductIncident,
    BehaviorEvaluation,
)


@admin.register(IncidentType)
class IncidentTypeAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "is_active"]
    list_filter = ["is_active"]


@admin.register(ConductIncident)
class ConductIncidentAdmin(admin.ModelAdmin):
    list_display = ["id", "enrollment", "academic_period", "incident_type", "incident_date", "severity"]
    list_filter = ["severity", "incident_date"]
    search_fields = ["enrollment__student__user__person__names", "description"]


@admin.register(BehaviorEvaluation)
class BehaviorEvaluationAdmin(admin.ModelAdmin):
    list_display = ["enrollment", "academic_period", "calculated_scale", "final_scale"]
    list_filter = ["academic_period"]