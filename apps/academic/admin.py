from django.contrib import admin
from .models import (
    Section, Subject, Config_Academic, Academic_Period, 
    Academic_Activity, Timing_Regime, Teacher_Subject_Section
)

@admin.register(Timing_Regime)
class TimingRegimeAdmin(admin.ModelAdmin):
    list_display = ("name", "school_year", "active")
    list_filter = ("school_year", "active")
    search_fields = ("name",)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("grade", "parallel", "level", "school_year", "capacity")
    list_filter = ("school_year", "level", "grade")
    search_fields = ("grade", "parallel", "level")


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "section", "weekly_hours", "active")
    list_filter = ("school_year", "section", "active")
    search_fields = ("name", "code")


class AcademicPeriodInline(admin.TabularInline):
    model = Academic_Period
    extra = 1


class AcademicActivityInline(admin.TabularInline):
    model = Academic_Activity
    extra = 1


@admin.register(Config_Academic)
class ConfigAcademicAdmin(admin.ModelAdmin):
    list_display = ("name", "institution", "school_year", "academic_period_type", "active")
    list_filter = ("institution", "active")
    search_fields = ("name",)
    inlines = [AcademicPeriodInline, AcademicActivityInline]


@admin.register(Academic_Period)
class AcademicPeriodAdmin(admin.ModelAdmin):
    list_display = ("name", "config_academic", "number", "start_date", "end_date", "active")
    list_filter = ("config_academic", "active")
    search_fields = ("name",)


@admin.register(Academic_Activity)
class AcademicActivityAdmin(admin.ModelAdmin):
    list_display = ("name", "config_academic", "value_max", "weight", "order", "active")
    list_filter = ("config_academic", "active")
    search_fields = ("name",)


@admin.register(Teacher_Subject_Section)
class TeacherSubjectSectionAdmin(admin.ModelAdmin):
    list_display = ("user", "subject", "section", "school_year", "active")
    list_filter = ("school_year", "section", "active")
    raw_id_fields = ("user", "subject", "section", "school_year")
    search_fields = ("user__names", "user__last_names", "subject__name")
