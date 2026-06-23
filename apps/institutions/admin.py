from django.contrib import admin
from .models import SchoolYear, AcademicLevel, AcademicSublevel, AcademicGrade, Section


@admin.register(SchoolYear)
class SchoolYearAdmin(admin.ModelAdmin):
    list_display = ("start_date", "end_date", "is_active")
    list_filter = ("is_active",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(AcademicLevel)
class AcademicLevelAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(AcademicSublevel)
class AcademicSublevelAdmin(admin.ModelAdmin):
    list_display = ("name", "academic_level")
    list_filter = ("academic_level",)


@admin.register(AcademicGrade)
class AcademicGradeAdmin(admin.ModelAdmin):
    list_display = ("name", "academic_sublevel")
    list_filter = ("academic_sublevel",)
    search_fields = ("name",)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("academic_grade", "parallel", "school_year", "capacity")
    list_filter = ("school_year", "academic_grade")
    search_fields = ("parallel",)
