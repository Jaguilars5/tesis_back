from django.contrib import admin

from .infrastructure.models import IncidentType


@admin.register(IncidentType)
class IncidentTypeAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("code", "name")
