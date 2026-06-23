from django.contrib import admin
from .models import Student, StudentRepresentative, Enrollment


class StudentAdmin(admin.ModelAdmin):
    list_display = ("student_code", "get_full_name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("user__person__names", "user__person__last_names", "user__person__document_number", "student_code")
    fieldsets = (
        ("Usuario", {"fields": ("user", "student_code")}),
        ("Estado", {"fields": ("is_active",)}),
    )

    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = "Nombre Completo"


class StudentRepresentativeAdmin(admin.ModelAdmin):
    list_display = ("get_student", "get_user", "kinship", "is_primary")
    list_filter = ("kinship", "is_primary")
    search_fields = ("student__user__person__names", "user__person__names", "user__person__last_names")
    readonly_fields = ("created_at",)
    fieldsets = (
        ("Relación", {"fields": ("student", "user", "kinship", "is_primary")}),
        ("Autorizaciones", {"fields": ("emergency_contact", "receives_notifications")}),
        ("Registro", {"fields": ("created_at",), "classes": ("collapse",)}),
    )

    def get_student(self, obj):
        return obj.student.get_full_name()
    get_student.short_description = "Estudiante"

    def get_user(self, obj):
        return obj.user.get_full_name() if obj.user else "-"
    get_user.short_description = "Representante"


admin.site.register(Student, StudentAdmin)
admin.site.register(StudentRepresentative, StudentRepresentativeAdmin)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "section", "enrollment_status", "school_year")
    list_filter = ("enrollment_status", "section__school_year")
    search_fields = ("student__user__person__names", "student__user__person__last_names")

