"""
Panel administrativo para el módulo Scheduling.
"""

from django.contrib import admin
from .models import (
    ScheduleTemplateConfig,
    TimeSlot,
    TeacherAvailability,
    ScheduleSlot,
    SubjectConstraint,
)


@admin.register(ScheduleTemplateConfig)
class ScheduleTemplateConfigAdmin(admin.ModelAdmin):
    list_display = ("id", "day_start_time", "total_slots_per_day")


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "day_of_week", "start_time", "end_time")
    list_filter = ("day_of_week",)


@admin.register(TeacherAvailability)
class TeacherAvailabilityAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "time_slot", "is_available")
    list_filter = ("is_available",)


@admin.register(ScheduleSlot)
class ScheduleSlotAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "teacher_subject_section",
        "time_slot",
        "classroom",
        "active",
    )
    list_filter = ("active",)


@admin.register(SubjectConstraint)
class SubjectConstraintAdmin(admin.ModelAdmin):
    list_display = ("id", "subject_academic_config", "required_consecutive_slots", "max_slots_per_day")
