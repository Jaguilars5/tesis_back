from django.contrib import admin
from .infrastructure.models import ClassSchedule


@admin.register(ClassSchedule)
class ClassScheduleAdmin(admin.ModelAdmin):
    list_display = ("teacher_subject_section", "get_day_of_week_display", "start_time", "end_time", "is_active")
    list_filter = ("day_of_week", "is_active")
    raw_id_fields = ("teacher_subject_section",)
    search_fields = ("teacher_subject_section__user__person__names", "teacher_subject_section__user__person__last_names")
