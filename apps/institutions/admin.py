from django.contrib import admin
from .models import School_Year, Classroom


@admin.register(School_Year)
class SchoolYearAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date", "active")
    list_filter = ("active",)
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ("name", "room_type", "capacity", "active")
    list_filter = ("active", "room_type")
    search_fields = ("name",)
