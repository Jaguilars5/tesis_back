from django.contrib import admin
from .infrastructure.models import SubjectOffering


@admin.register(SubjectOffering)
class SubjectOfferingAdmin(admin.ModelAdmin):
    list_display = ("school_year", "section", "subject_academic_config", "is_active")
