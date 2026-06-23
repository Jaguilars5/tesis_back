from django.contrib import admin
from .models import (
    Subject,
    AcademicPeriod,
    TeacherSubjectSection,
    SubjectAcademicConfig,
    SubjectOffering,
    PeriodType,
    ClassSchedule,
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
        "is_active",
    )


@admin.register(SubjectOffering)
class SubjectOfferingAdmin(admin.ModelAdmin):
    list_display = ("school_year", "section", "subject_academic_config", "is_active")


@admin.register(PeriodType)
class PeriodTypeAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "divisions_per_year", "is_active")
    list_filter = ("is_active",)
    search_fields = ("code", "name")


@admin.register(ClassSchedule)
class ClassScheduleAdmin(admin.ModelAdmin):
    list_display = (
        "teacher_subject_section",
        "get_day_of_week_display",
        "start_time",
        "end_time",
        "is_active",
    )
    list_filter = ("day_of_week", "is_active")
    raw_id_fields = ("teacher_subject_section",)
    search_fields = (
        "teacher_subject_section__user__person__names",
        "teacher_subject_section__user__person__last_names",
    )
