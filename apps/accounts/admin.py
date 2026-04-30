"""
Registra los modelos del módulo accounts en el panel de administración.

Útil para inspeccionar datos y gestionar manualmente conflictos.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Permission, Role, RolePermission, UserPermission, User


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """Admin para Permission."""

    list_display = ["codename", "description", "module", "created_at"]
    list_filter = ["module", "created_at"]
    search_fields = ["codename", "description"]
    ordering = ["codename"]
    readonly_fields = ["created_at", "updated_at"]
    fields = ["codename", "description", "module", "created_at", "updated_at"]


class RolePermissionInline(admin.TabularInline):
    """Inline para RolePermission."""

    model = RolePermission
    extra = 1
    autocomplete_fields = ["permission"]


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Admin para Role."""

    list_display = [
        "name",
        "description",
        "active_status",
        "permission_count",
        "user_count",
        "created_at",
    ]
    list_filter = ["active", "created_at"]
    search_fields = ["name", "description"]
    readonly_fields = ["created_at", "updated_at"]

    inlines = [RolePermissionInline]

    fieldsets = (
        ("Información básica", {"fields": ("name", "description", "active")}),
        (
            "Auditoría",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def active_status(self, obj):
        """Muestra estado activo con colores."""
        if obj.active:
            return format_html('<span style="color: green;">✓ Activo</span>')
        return format_html('<span style="color: red;">✗ Inactivo</span>')

    active_status.short_description = "Estado"

    def permission_count(self, obj):
        """Muestra cantidad de permisos."""
        return obj.role_permissions.count()

    permission_count.short_description = "Permisos"

    def user_count(self, obj):
        """Muestra cantidad de usuarios con este rol."""
        return obj.users.count()

    user_count.short_description = "Usuarios"


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    """Admin para RolePermission."""

    list_display = ["role", "permission", "created_at"]
    list_filter = ["role", "permission", "created_at"]
    search_fields = ["role__name", "permission__codename"]
    readonly_fields = ["created_at"]
    raw_id_fields = ["role", "permission"]


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Admin para User."""

    list_display = [
        "email",
        "full_name",
        "dni",
        "role",
        "institution",
        "active_status",
        "created_at",
    ]
    list_filter = ["active", "role", "institution", "created_at"]
    search_fields = ["email", "names", "last_names", "dni"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        ("Información personal", {"fields": ("dni", "names", "last_names", "email")}),
        ("Acceso", {"fields": ("role", "institution", "active")}),
        ("Seguridad", {"fields": ("password",), "classes": ("collapse",)}),
        (
            "Auditoría",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    raw_id_fields = ["role", "institution"]

    def full_name(self, obj):
        """Retorna el nombre completo."""
        return f"{obj.names} {obj.last_names}"

    full_name.short_description = "Nombre completo"

    def active_status(self, obj):
        """Muestra estado activo con colores."""
        if obj.active:
            return format_html('<span style="color: green;">✓ Activo</span>')
        return format_html('<span style="color: red;">✗ Inactivo</span>')

    active_status.short_description = "Estado"


@admin.register(UserPermission)
class UserPermissionAdmin(admin.ModelAdmin):
    """Admin para UserPermission."""

    list_display = [
        "user",
        "permission",
        "granted_status",
        "reason_preview",
        "expires_at",
        "created_at",
    ]
    list_filter = ["granted", "created_at", "expires_at"]
    search_fields = ["user__email", "permission__codename", "reason"]
    readonly_fields = ["created_at", "updated_at"]
    autocomplete_fields = ["permission"]
    raw_id_fields = ["user", "granted_by"]

    fieldsets = (
        ("Relación", {"fields": ("user", "permission")}),
        ("Detalles", {"fields": ("granted", "reason", "expires_at", "granted_by")}),
        (
            "Auditoría",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def granted_status(self, obj):
        """Muestra estado otorgado/revocado con colores."""
        if obj.granted:
            return format_html('<span style="color: green;">✓ Otorgado</span>')
        return format_html('<span style="color: red;">✗ Revocado</span>')

    granted_status.short_description = "Estado"

    def reason_preview(self, obj):
        """Muestra vista previa de la razón."""
        if obj.reason:
            return obj.reason[:50] + ("..." if len(obj.reason) > 50 else "")
        return "-"

    reason_preview.short_description = "Razón"


