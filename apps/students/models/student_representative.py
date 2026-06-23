from django.db import models
from django.db.models import UniqueConstraint
from apps.core.models import TimeStampedModel


class StudentRepresentative(TimeStampedModel):
    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        related_name="representatives_set",
        verbose_name="Estudiante",
    )
    kinship = models.ForeignKey(
        "students.Kinship",
        on_delete=models.PROTECT,
        verbose_name="Parentesco",
    )
    user = models.ForeignKey(
        "iam.User",
        on_delete=models.CASCADE,
        related_name="student_representatives",
        null=False,
        verbose_name="Usuario del Representante",
    )

    is_primary = models.BooleanField(default=False, verbose_name="Es Principal")
    emergency_contact = models.BooleanField(
        default=False, verbose_name="Contacto de Emergencia"
    )
    receives_notifications = models.BooleanField(
        default=True, verbose_name="Recibe Notificaciones"
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "students"
        verbose_name = "Relación Estudiante-Representante"
        verbose_name_plural = "Relaciones Estudiante-Representante"
        constraints = [
            UniqueConstraint(fields=["student", "user"], name="unique_student_user"),
            UniqueConstraint(
                fields=["student"],
                condition=models.Q(is_primary=True),
                name="unique_primary_representative_per_student",
            ),
        ]
        ordering = ["-is_primary", "-created_at"]

    def __str__(self):
        return f"{self.user.get_full_name()}"

    @property
    def representative_student(self):
        return f"{self.student.get_full_name()} - {self.kinship.name} ({'Principal' if self.is_primary else 'Secundario'})"
