from django.db import models
from apps.core.models import TimeStampedModel


class RolePermission(TimeStampedModel):
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
    class Meta:
        app_label = "iam"
        verbose_name = "Permiso del Rol"
        verbose_name_plural = "Permisos del Rol"
        constraints = [
            models.UniqueConstraint(fields=["role", "permission"], name="unique_role_permission"),
        ]
        indexes = [
            models.Index(fields=["role"]),
            models.Index(fields=["permission"]),
        ]

    def __str__(self):
        return f"{self.role.name} → {self.permission.code}"
