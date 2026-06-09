from django.contrib import admin
from .models import User, Role, Permission, UserRole, RolePermission


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["email", "is_active", "is_staff", "is_superuser", "created_at"]
    list_filter = ["is_active", "is_staff", "is_superuser"]
    search_fields = ["email", "person__names", "person__last_names"]


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name", "code"]


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ["code", "module"]
    list_filter = ["module"]
    search_fields = ["code"]


admin.site.register(UserRole)
admin.site.register(RolePermission)
