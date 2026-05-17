from django.db import models


class RolePermission(models.Model):
    """
    Tabla intermedia explícita que vincula Role ↔ Permission.

    Permite tener control granular sobre qué permisos tiene cada rol
    sin usar la convención automática de Django.
    """

    role = models.ForeignKey(
        "Role",
        on_delete=models.CASCADE,
        related_name="role_permissions",
        verbose_name="Rol",
        help_text="El rol que recibe el permiso",
    )
    permission = models.ForeignKey(
        "Permission",
        on_delete=models.CASCADE,
        related_name="permission_roles",
        verbose_name="Permiso",
        help_text="El permiso otorgado",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )

    class Meta:
        app_label = "accounts"
        verbose_name = "Permiso del Rol"
        verbose_name_plural = "Permisos del Rol"
        unique_together = ("role", "permission")
        indexes = [
            models.Index(fields=["role"]),
            models.Index(fields=["permission"]),
        ]

    def __str__(self):
        return f"{self.role.name} → {self.permission.code}"
