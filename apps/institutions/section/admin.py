from django.contrib import admin

from .infrastructure.models import Section


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("parallel", "school_year", "academic_grade", "capacity", "is_active")
    list_filter = ("is_active",)
    search_fields = ("parallel",)
