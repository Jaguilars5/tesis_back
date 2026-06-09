from django.db import models
from apps.core.models import TimeStampedModel


class UserRole(TimeStampedModel):
    user = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        related_name="user_roles",
        verbose_name="Usuario",
    )
    role = models.ForeignKey(
        "Role",
        on_delete=models.CASCADE,
        related_name="user_roles",
        verbose_name="Rol",
    )
    assigned_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Asignado en"
    )
    expires_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Expira en"
    )

    class Meta:
        app_label = "iam"
        verbose_name = "Rol del Usuario"
        verbose_name_plural = "Roles del Usuario"
        unique_together = ("user", "role")

    def __str__(self):
        return f"{self.user} → {self.role.name}"
