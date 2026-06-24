from django.contrib import admin
from .infrastructure.models import PeriodType


@admin.register(PeriodType)
class PeriodTypeAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "divisions_per_year", "is_active")
    list_filter = ("is_active",)
    search_fields = ("code", "name")
