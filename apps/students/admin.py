from django.contrib import admin
from .models import Student, Representative, Student_Representative


class StudentAdmin(admin.ModelAdmin):
    list_display = ("dni", "get_full_name", "section", "enrollment_number", "active")
    list_filter = ("section", "active", "enrollment_date")
    search_fields = ("names", "last_names", "dni")
    readonly_fields = ("enrollment_date", "created_at", "updated_at")
    fieldsets = (
        (
            "Información Personal",
            {"fields": ("dni", "names", "last_names", "birth_date")},
        ),
        ("Matrícula", {"fields": ("section", "enrollment_number", "enrollment_date")}),
        (
            "Sincronización",
            {"fields": ("device_origin", "sync_version"), "classes": ("collapse",)},
        ),
        ("Estado", {"fields": ("active", "created_at", "updated_at")}),
    )

    def get_full_name(self, obj):
        return obj.get_full_name()

    get_full_name.short_description = "Nombre Completo"


class RepresentativeAdmin(admin.ModelAdmin):
    list_display = ("dni", "get_full_name", "phone", "active")
    list_filter = ("active",)
    search_fields = ("names", "last_names", "dni", "phone")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Información Personal", {"fields": ("dni", "names", "last_names")}),
        ("Contacto", {"fields": ("phone", "email", "address")}),
        ("Estado", {"fields": ("active", "created_at", "updated_at")}),
    )

    def get_full_name(self, obj):
        return obj.get_full_name()

    get_full_name.short_description = "Nombre Completo"


class StudentRepresentativeAdmin(admin.ModelAdmin):
    list_display = (
        "get_student",
        "get_representative",
        "kinship",
        "is_primary",
        "can_pickup",
        "emergency_contact",
    )
    list_filter = ("kinship", "is_primary", "can_pickup", "emergency_contact", "receives_notifications")
    search_fields = (
        "student__names",
        "student__last_names",
        "representative__names",
        "representative__last_names",
    )
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Relación", {"fields": ("student", "representative", "kinship", "is_primary")}),
        (
            "Autorizaciones y Notificaciones",
            {
                "fields": (
                    "can_pickup",
                    "emergency_contact",
                    "receives_notifications",
                )
            },
        ),
        (
            "Registro",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_student(self, obj):
        return obj.student.get_full_name()

    get_student.short_description = "Estudiante"

    def get_representative(self, obj):
        return obj.representative.get_full_name()

    get_representative.short_description = "Representante"


admin.site.register(Student, StudentAdmin)
admin.site.register(Representative, RepresentativeAdmin)
admin.site.register(Student_Representative, StudentRepresentativeAdmin)
