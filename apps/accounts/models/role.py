from django.db import models
from .permission import Permission


class Role(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre del Rol",
        help_text="Nombre único del rol",
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Código del Rol",
        help_text="Código único del rol (DOCENTE, ADMIN, etc)",
        null=True,
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Descripción",
        help_text="Descripción del rol",
    )
    active = models.BooleanField(
        default=True,
        verbose_name="Activo",
        help_text="Indica si el rol puede ser asignado a nuevos usuarios",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de Actualización"
    )

    class Meta:
        app_label = "accounts"
        verbose_name = "Rol"
        verbose_name_plural = "Roles"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["active"]),
        ]

    def __str__(self):
        return self.name

    def get_all_permissions(self):
        """
        Retorna todos los Permission objects asociados a este rol
        via RolePermission.
        """
        from .role_permission import RolePermission

        return Permission.objects.filter(permission_roles__role=self).distinct()
