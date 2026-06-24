from django.contrib import admin

from .infrastructure.models import AcademicSublevel


@admin.register(AcademicSublevel)
class AcademicSublevelAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "academic_level", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "code")
