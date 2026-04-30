from django.db import models


class UserPermission(models.Model):
    """
    Permisos excepcionales a nivel de usuario.

    Permite otorgar o revocar permisos específicos a un usuario,
    independientemente de su rol.

    - granted=True  → el usuario TIENE este permiso (aunque el rol no lo tenga)
    - granted=False → el usuario NO TIENE este permiso (aunque el rol sí lo tenga)

    Si no existe un registro para (user, permission), el permiso se hereda del rol.

    reason: Campo auditable que documenta por qué se otorgó/revocó.
    expires_at: Opcional. Si se especifica, el permiso expira en esa fecha.
    granted_by: FK a User que hizo el cambio (auditoría).
    """

    user = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        related_name="user_permissions_set",
        verbose_name="Usuario",
        help_text="Usuario al que se aplica el permiso",
    )
    permission = models.ForeignKey(
        "Permission",
        on_delete=models.CASCADE,
        related_name="user_permissions_set",
        verbose_name="Permiso",
        help_text="El permiso otorgado o revocado",
    )
    granted = models.BooleanField(
        default=True,
        verbose_name="Otorgado",
        help_text="Verdadero = otorgado, Falso = revocado",
    )
    reason = models.TextField(
        blank=True,
        verbose_name="Razón",
        help_text="Razón del cambio de permiso (auditoría)",
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Expiración",
        help_text="Fecha de expiración del permiso (opcional)",
    )
    granted_by = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="granted_user_permissions",
        verbose_name="Otorgado por",
        help_text="Usuario que otorgó/revocó este permiso",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de Actualización"
    )

    class Meta:
        app_label = "accounts"
        verbose_name = "Permiso del Usuario"
        verbose_name_plural = "Permisos del Usuario"
        unique_together = ("user", "permission")
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["permission"]),
            models.Index(fields=["granted"]),
        ]

    def __str__(self):
        state = "granted" if self.granted else "revoked"
        return f"{self.user} — {self.permission.codename} [{state}]"

    def is_expired(self):
        """
        Verifica si el permiso ha expirado.
        """
        if self.expires_at is None:
            return False
        from django.utils import timezone

        return timezone.now() > self.expires_at
