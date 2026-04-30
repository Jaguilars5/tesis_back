from django.db import models
import uuid


class Student(models.Model):
    """Modelo de estudiante"""

    uuid = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, verbose_name="UUID"
    )
    dni = models.CharField(
        max_length=13, unique=True, verbose_name="Número de Documento"
    )
    names = models.CharField(max_length=100, verbose_name="Nombres")
    last_names = models.CharField(max_length=100, verbose_name="Apellidos")
    birth_date = models.DateField(verbose_name="Fecha de Nacimiento")
    section = models.ForeignKey(
        "academic.Section",
        on_delete=models.CASCADE,
        related_name="students",
        verbose_name="Sección",
    )
    enrollment_number = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Número de Matrícula",
    )
    enrollment_date = models.DateField(
        auto_now_add=True, verbose_name="Fecha de Matrícula"
    )
    active = models.BooleanField(default=True, verbose_name="Activo")

    # Sync & Audit Fields
    sync_status = models.CharField(
        max_length=20, default="pending", verbose_name="Estado de Sincronización"
    )
    synced_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Sincronizado en"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de Actualización"
    )
    deleted_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Fecha de Eliminación"
    )
    sync_version = models.PositiveIntegerField(
        default=0, verbose_name="Versión de Sincronización"
    )
    device_origin = models.CharField(
        max_length=40, null=True, blank=True, verbose_name="Dispositivo de Origen"
    )

    class Meta:
        app_label = "students"
        verbose_name = "Estudiante"
        verbose_name_plural = "Estudiantes"
        ordering = ["last_names", "names"]
        indexes = [
            models.Index(fields=["dni"]),
            models.Index(fields=["section", "active"]),
        ]

    def __str__(self):
        return f"{self.names} {self.last_names}"

    def get_full_name(self):
        """Retorna el nombre completo"""
        return f"{self.names} {self.last_names}"

    def get_age(self):
        """Calcula la edad aproximada"""
        from datetime import date

        today = date.today()
        age = (
            today.year
            - self.birth_date.year
            - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        )
        return age
