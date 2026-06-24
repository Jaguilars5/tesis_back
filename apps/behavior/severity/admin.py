from django.contrib import admin

from .infrastructure.models import Severity


@admin.register(Severity)
class SeverityAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("code", "name")
