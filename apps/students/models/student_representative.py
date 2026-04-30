from django.db import models


class Student_Representative(models.Model):
    """Tabla de unión: Estudiante - Representante (relación N:N)"""

    KINSHIP_CHOICES = [
        ("Padre", "Padre"),
        ("Madre", "Madre"),
        ("Abuelo/a", "Abuelo/a"),
        ("Tío/a", "Tío/a"),
        ("Hermano/a Mayor", "Hermano/a Mayor"),
        ("Otro", "Otro"),
    ]

    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        related_name="representatives_set",
        verbose_name="Estudiante",
    )
    representative = models.ForeignKey(
        "students.Representative",
        on_delete=models.CASCADE,
        related_name="students_set",
        verbose_name="Representante",
    )
    kinship = models.CharField(
        max_length=30,
        choices=KINSHIP_CHOICES,
        default="Padre",
        verbose_name="Parentesco",
    )
    is_primary = models.BooleanField(default=False, verbose_name="Es Principal")
    can_pickup = models.BooleanField(
        default=True, verbose_name="Puede Recoger Estudiante"
    )
    emergency_contact = models.BooleanField(
        default=False, verbose_name="Contacto de Emergencia"
    )
    receives_notifications = models.BooleanField(
        default=True, verbose_name="Recibe Notificaciones"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de Actualización"
    )

    class Meta:
        app_label = "students"
        verbose_name = "Relación Estudiante-Representante"
        verbose_name_plural = "Relaciones Estudiante-Representante"
        unique_together = ("student", "representative")
        ordering = ["-is_primary", "-created_at"]
        indexes = [
            models.Index(fields=["student", "is_primary"]),
            models.Index(fields=["representative"]),
        ]

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.representative.get_full_name()}"
