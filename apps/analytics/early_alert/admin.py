"""
Panel administrativo para alertas tempranas.
"""

from django.contrib import admin

from .infrastructure.models import EarlyAlert


@admin.register(EarlyAlert)
class EarlyAlertAdmin(admin.ModelAdmin):
    list_display = (
        "enrollment",
        "academic_period",
        "alert_type",
        "urgency_level",
        "attended",
        "detected_at",
    )
    list_filter = ("alert_type", "urgency_level", "attended", "academic_period")
    search_fields = (
        "enrollment__student__user__person__names",
        "enrollment__student__user__person__last_names",
        "description",
    )
