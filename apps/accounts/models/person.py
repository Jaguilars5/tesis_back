from django.db import models


class Person(models.Model):
    document_type = models.ForeignKey(
        "institutions.DocumentType",
        on_delete=models.PROTECT,
        verbose_name="Tipo de Documento",
        null=True,
    )
    document_number = models.CharField(
        max_length=20, unique=True, verbose_name="Número de Documento"
    )
    names = models.CharField(max_length=100, verbose_name="Nombres")
    last_names = models.CharField(max_length=100, verbose_name="Apellidos")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Fecha de Nacimiento")
    email = models.EmailField(blank=True, verbose_name="Correo Electrónico")
    phone = models.CharField(max_length=15, blank=True, verbose_name="Teléfono")
    active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Eliminación")

    class Meta:
        app_label = "accounts"
        verbose_name = "Persona"
        verbose_name_plural = "Personas"
        ordering = ["last_names", "names"]
        indexes = [
            models.Index(fields=["document_number"]),
            models.Index(fields=["active"]),
        ]

    def __str__(self):
        return f"{self.names} {self.last_names}"

    def get_full_name(self):
        return f"{self.names} {self.last_names}"
