from django.contrib import admin
from .infrastructure.models import AcademicPeriod


@admin.register(AcademicPeriod)
class AcademicPeriodAdmin(admin.ModelAdmin):
    list_display = ("name", "school_year", "start_date", "end_date", "is_regular_period")
    list_filter = ("school_year",)
    search_fields = ("name",)
