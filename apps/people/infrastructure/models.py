from django.db import models
from django.utils import timezone
from apps.core.models import TimeStampedModel


class City(TimeStampedModel):
    name = models.CharField(max_length=100, verbose_name="Nombre de la Ciudad")
    code = models.CharField(
        max_length=10, unique=True, verbose_name="Código de la Ciudad"
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "people"
        db_table = "people_city"
        verbose_name = "Ciudad"
        verbose_name_plural = "Ciudades"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Parish(TimeStampedModel):
    PARISH_TYPES = [
        ("URBANA", "Urbana"),
        ("RURAL", "Rural"),
    ]
    name = models.CharField(max_length=100, verbose_name="Nombre de la Parroquia")
    code = models.CharField(
        max_length=10, unique=True, verbose_name="Código de la Parroquia"
    )
    parish_type = models.CharField(
        max_length=10, choices=PARISH_TYPES, verbose_name="Tipo de Parroquia"
    )
    city = models.ForeignKey(
        "people.City",
        on_delete=models.PROTECT,
        verbose_name="Ciudad",
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "people"
        db_table = "people_parish"
        verbose_name = "Parroquia"
        verbose_name_plural = "Parroquias"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_parish_type_display()})"


class DocumentType(TimeStampedModel):
    code = models.CharField(max_length=10, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "people"
        db_table = "people_document_type"
        verbose_name = "Tipo de Documento"
        verbose_name_plural = "Tipos de Documento"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Person(TimeStampedModel):
    parish = models.ForeignKey(
        "people.Parish",
        on_delete=models.PROTECT,
        verbose_name="Parroquia de Residencia",
        null=True,
    )
    document_type = models.ForeignKey(
        "people.DocumentType",
        on_delete=models.PROTECT,
        verbose_name="Tipo de Documento",
        null=True,
    )
    document_number = models.CharField(
        max_length=20, unique=True, verbose_name="Número de Documento"
    )
    birth_date = models.DateField(verbose_name="Fecha de Nacimiento")
    names = models.CharField(max_length=100, verbose_name="Nombres")
    last_names = models.CharField(max_length=100, verbose_name="Apellidos")

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
