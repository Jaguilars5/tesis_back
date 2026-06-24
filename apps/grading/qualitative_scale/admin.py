from django.contrib import admin

from .infrastructure.models import QualitativeScale, QualitativeScaleSublevel


@admin.register(QualitativeScale)
class QualitativeScaleAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "numeric_equivalence", "is_active")
    list_filter = ("is_active",)
    search_fields = ("code", "name")


@admin.register(QualitativeScaleSublevel)
class QualitativeScaleSublevelAdmin(admin.ModelAdmin):
    list_display = ("scale", "sublevel", "is_active")
    list_filter = ("is_active",)
