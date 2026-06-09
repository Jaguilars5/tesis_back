from django.contrib import admin
from .models import (
    Subject,
    AcademicPeriod,
    TeacherSubjectSection,
    SubjectAcademicConfig,
    SubjectOffering,
    InterdisciplinaryProject,
    SubjectProject,
    PeriodType,
)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "code")


@admin.register(AcademicPeriod)
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


@admin.register(TeacherSubjectSection)
class TeacherSubjectSectionAdmin(admin.ModelAdmin):
    list_display = ("user", "subject_offering", "is_active")
    list_filter = ("is_active",)
    raw_id_fields = ("user", "subject_offering")
    search_fields = ("user__person__names", "user__person__last_names")


@admin.register(SubjectAcademicConfig)
class SubjectAcademicConfigAdmin(admin.ModelAdmin):
    list_display = (
        "subject",
        "academic_grade",
        "weekly_hours",
        "pedagogical_order",
        "is_active",
    )


@admin.register(SubjectOffering)
class SubjectOfferingAdmin(admin.ModelAdmin):
    list_display = ("school_year", "section", "subject_academic_config", "is_active")


@admin.register(InterdisciplinaryProject)
class InterdisciplinaryProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "academic_period", "start_date", "delivery_date", "is_active")
    list_filter = ("is_active", "academic_period")
    search_fields = ("title",)


@admin.register(SubjectProject)
class SubjectProjectAdmin(admin.ModelAdmin):
    list_display = ("interdisciplinary_project", "subject_offering")


@admin.register(PeriodType)
class PeriodTypeAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    search_fields = ("code", "name")
