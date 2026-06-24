from django.contrib import admin

from .infrastructure.models import ConductIncident


@admin.register(ConductIncident)
class ConductIncidentAdmin(admin.ModelAdmin):
    list_display = ["id", "enrollment", "academic_period", "incident_type", "incident_date", "severity"]
    list_filter = ["severity", "incident_date"]
    search_fields = ["enrollment__student__user__person__names", "description"]
