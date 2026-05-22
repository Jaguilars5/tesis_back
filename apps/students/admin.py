from django.contrib import admin
from .models import Student, Student_Representative


class StudentAdmin(admin.ModelAdmin):
    list_display = ("student_code", "get_full_name", "active")
    list_filter = ("active",)
    search_fields = ("person__names", "person__last_names", "person__document_number", "student_code")
    fieldsets = (
        ("Persona", {"fields": ("person", "student_code")}),
        ("Estado", {"fields": ("active",)}),
    )

    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = "Nombre Completo"


class StudentRepresentativeAdmin(admin.ModelAdmin):
    list_display = ("get_student", "get_person", "kinship", "is_primary")
    list_filter = ("kinship", "is_primary")
    search_fields = ("student__person__names", "person__names", "person__last_names")
    readonly_fields = ("created_at",)
    fieldsets = (
        ("Relación", {"fields": ("student", "person", "kinship", "is_primary")}),
        ("Autorizaciones", {"fields": ("can_pickup", "emergency_contact", "receives_notifications")}),
        ("Registro", {"fields": ("created_at",), "classes": ("collapse",)}),
    )

    def get_student(self, obj):
        return obj.student.get_full_name()
    get_student.short_description = "Estudiante"

    def get_person(self, obj):
        return obj.person.get_full_name() if obj.person else "-"
    get_person.short_description = "Persona"


admin.site.register(Student, StudentAdmin)
admin.site.register(Student_Representative, StudentRepresentativeAdmin)
