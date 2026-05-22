from django.contrib import admin
from django.utils.html import format_html
from .models import Permission, Person, Role, RolePermission, User, UserRole


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ["document_number", "names", "last_names", "email", "active"]
    list_filter = ["active"]
    search_fields = ["document_number", "names", "last_names", "email"]


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ["code", "description", "module", "created_at"]
    list_filter = ["module", "created_at"]
    search_fields = ["code", "description"]
    ordering = ["code"]
    readonly_fields = ["created_at", "updated_at"]
    fields = ["code", "description", "module", "created_at", "updated_at"]


class RolePermissionInline(admin.TabularInline):
    model = RolePermission
    extra = 1
    autocomplete_fields = ["permission"]


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "description", "active_status", "permission_count", "created_at"]
    list_filter = ["active", "created_at"]
    search_fields = ["name", "code", "description"]
    readonly_fields = ["created_at", "updated_at"]
    inlines = [RolePermissionInline]
    fieldsets = (
        ("Información básica", {"fields": ("name", "code", "description", "active")}),
        ("Auditoría", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def active_status(self, obj):
        if obj.active:
            return format_html('<span style="color: green;">✓ Activo</span>')
        return format_html('<span style="color: red;">✗ Inactivo</span>')
    active_status.short_description = "Estado"

    def permission_count(self, obj):
        return obj.role_permissions.count()
    permission_count.short_description = "Permisos"


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ["role", "permission", "created_at"]
    list_filter = ["role", "permission", "created_at"]
    search_fields = ["role__name", "permission__code"]
    readonly_fields = ["created_at"]
    raw_id_fields = ["role", "permission"]


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["email_display", "full_name", "active_status", "created_at"]
    list_filter = ["active", "created_at"]
    search_fields = ["person__names", "person__last_names", "person__email", "person__document_number"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        ("Persona", {"fields": ("person",)}),
        ("Acceso", {"fields": ("active",)}),
        ("Seguridad", {"fields": ("password",), "classes": ("collapse",)}),
        ("Auditoría", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
    raw_id_fields = ["person"]

    def email_display(self, obj):
        if obj.person and obj.person.email:
            return obj.person.email
        return "-"
    email_display.short_description = "Email"

    def full_name(self, obj):
        if obj.person:
            return f"{obj.person.names} {obj.person.last_names}"
        return "-"
    full_name.short_description = "Nombre completo"

    def active_status(self, obj):
        if obj.active:
            return format_html('<span style="color: green;">✓ Activo</span>')
        return format_html('<span style="color: red;">✗ Inactivo</span>')
    active_status.short_description = "Estado"


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ["user", "role", "assigned_at", "expires_at"]
    list_filter = ["role", "assigned_at"]
    raw_id_fields = ["user", "role"]

