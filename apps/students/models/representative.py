from django.db import models


class Representative(models.Model):
    """Modelo de representante o acudiente del estudiante"""

    names = models.CharField(max_length=100, verbose_name="Nombres")
    last_names = models.CharField(max_length=100, verbose_name="Apellidos")
    dni = models.CharField(
        max_length=13, unique=True, verbose_name="Número de Documento"
    )
    email = models.CharField(
        max_length=150, null=True, blank=True, verbose_name="Correo Electrónico"
    )
    phone = models.CharField(max_length=15, verbose_name="Teléfono")
    address = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Dirección"
    )
    active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de Actualización"
    )

    class Meta:
        app_label = "students"
        verbose_name = "Representante"
        verbose_name_plural = "Representantes"
        ordering = ["last_names", "names"]
        indexes = [
            models.Index(fields=["dni"]),
            models.Index(fields=["active"]),
        ]

    def __str__(self):
        return f"{self.names} {self.last_names}"

    def get_full_name(self):
        """Retorna el nombre completo"""
        return f"{self.names} {self.last_names}"
