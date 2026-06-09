from django.db import models
from apps.core.models import TimeStampedModel


class StudentRepresentative(TimeStampedModel):
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
    person = models.ForeignKey(
        "people.Person",
        on_delete=models.CASCADE,
        related_name="student_representatives",
        null=True, blank=True,
        verbose_name="Persona",
    )
    kinship = models.CharField(
        max_length=30,
        choices=KINSHIP_CHOICES,
        default="Padre",
        verbose_name="Parentesco",
    )
    is_primary = models.BooleanField(default=False, verbose_name="Es Principal")
    can_pickup = models.BooleanField(default=True, verbose_name="Puede Recoger")
    emergency_contact = models.BooleanField(default=False, verbose_name="Contacto de Emergencia")
    receives_notifications = models.BooleanField(default=True, verbose_name="Recibe Notificaciones")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    class Meta:
        app_label = "students"
        verbose_name = "Relación Estudiante-Representante"
        verbose_name_plural = "Relaciones Estudiante-Representante"
        unique_together = ("student", "person")
        ordering = ["-is_primary", "-created_at"]

    def __str__(self):
        return f"{self.student} - {self.person.get_full_name()}"
