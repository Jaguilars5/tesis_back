from django.contrib import admin
from .infrastructure.models import TeacherSubjectSection


@admin.register(TeacherSubjectSection)
class TeacherSubjectSectionAdmin(admin.ModelAdmin):
    list_display = ("user", "subject_offering", "is_active")
    list_filter = ("is_active",)
    raw_id_fields = ("user", "subject_offering")
    search_fields = ("user__person__names", "user__person__last_names")
