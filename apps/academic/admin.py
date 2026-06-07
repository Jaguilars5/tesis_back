from django.contrib import admin
from apps.institutions.models import Section
from .models import (
    Subject,
    Academic_Period,
    Teacher_Subject_Section,
    SubjectAcademicConfig,
    SubjectOffering,
)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("academic_grade", "parallel", "school_year", "capacity")
    list_filter = ("school_year", "academic_grade")
    search_fields = ("parallel",)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "active")
    list_filter = ("active",)
    search_fields = ("name", "code")


@admin.register(Academic_Period)
class AcademicPeriodAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "school_year",
        "start_date",
        "end_date",
        "is_regular_period",
    )
    list_filter = ("school_year",)
    search_fields = ("name",)


@admin.register(Teacher_Subject_Section)
class TeacherSubjectSectionAdmin(admin.ModelAdmin):
    list_display = ("user", "subject_offering", "active")
    list_filter = ("active",)
    raw_id_fields = ("user", "subject_offering")
    search_fields = ("user__person__names", "user__person__last_names")


@admin.register(SubjectAcademicConfig)
class SubjectAcademicConfigAdmin(admin.ModelAdmin):
    list_display = (
        "subject",
        "academic_grade",
        "weekly_hours",
        "pedagogical_order",
        "active",
    )


@admin.register(SubjectOffering)
class SubjectOfferingAdmin(admin.ModelAdmin):
    list_display = ("school_year", "section", "subject_academic_config", "active")
