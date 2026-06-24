from django.contrib import admin
from .infrastructure.models import SubjectAcademicConfig


@admin.register(SubjectAcademicConfig)
class SubjectAcademicConfigAdmin(admin.ModelAdmin):
    list_display = ("subject", "academic_grade", "weekly_hours", "is_active")
