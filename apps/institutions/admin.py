from django.contrib import admin
from .models import Institution, School_Year, Classroom

@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "address", "city", "active")
    list_filter = ("active",)
    search_fields = ("name", "code", "address", "city")
    readonly_fields = ("created_at", "updated_at")


@admin.register(School_Year)
class SchoolYearAdmin(admin.ModelAdmin):
    list_display = ("name", "institution", "start_date", "end_date", "active")
    list_filter = ("institution", "active")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ("name", "institution", "room_type", "capacity", "active")
    list_filter = ("institution", "active", "room_type")
    search_fields = ("name",)

