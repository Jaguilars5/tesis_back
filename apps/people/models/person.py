from django.db import models
from django.utils import timezone
from apps.core.models import TimeStampedModel


class Person(TimeStampedModel):
    document_type = models.ForeignKey(
        "people.DocumentType",
        on_delete=models.PROTECT,
        verbose_name="Tipo de Documento",
        null=True,
    )
    document_number = models.CharField(
        max_length=20, unique=True, verbose_name="Número de Documento"
    )
    names = models.CharField(max_length=100, verbose_name="Nombres")
    last_names = models.CharField(max_length=100, verbose_name="Apellidos")
    birth_date = models.DateField(
        null=True, blank=True, verbose_name="Fecha de Nacimiento"
    )
    email = models.EmailField(blank=True, verbose_name="Correo Electrónico")
    phone = models.CharField(max_length=15, blank=True, verbose_name="Teléfono")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    class Meta:
        app_label = "people"
        verbose_name = "Persona"
        verbose_name_plural = "Personas"
        ordering = ["last_names", "names"]
        indexes = [
            models.Index(fields=["document_number"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.names} {self.last_names}"

    def get_full_name(self):
        return f"{self.names} {self.last_names}"

    def get_age(self):
        if self.birth_date:
            today = timezone.now().date()
            age = today.year - self.birth_date.year
            if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
                age -= 1
            return age
        return None
