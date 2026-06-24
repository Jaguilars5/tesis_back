from django.db import models
from django.db.models import TextChoices, UniqueConstraint
from apps.core.models import TimeStampedModel
from apps.integration.models.syncable_mixin import SyncableModel


class EnrollmentStatusChoices(TextChoices):
    ACTIVE = "ACT", "Activa"
    WITHDRAWN = "RET", "Retirado"
    TRANSFERRED = "TRS", "Transferido"
    SUSPENDED = "SUS", "Suspendido"
    GRADUATED = "GRA", "Graduado"
    INACTIVE = "INA", "Inactivo"


class Enrollment(TimeStampedModel, SyncableModel):
    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name="Estudiante",
    )
    withdrawal_reason = models.ForeignKey(
        "students.WithdrawalReason",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Motivo de Retiro",
    )
    section = models.ForeignKey(
        "institutions_section.Section",
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name="Sección",
    )
    enrollment_date = models.DateField(
        verbose_name="Fecha de Matrícula",
        auto_now_add=True,
    )
    enrollment_status = models.CharField(
        max_length=5,
        choices=EnrollmentStatusChoices.choices,
        verbose_name="Estado de Matrícula",
    )

    withdrawal_date = models.DateField(
        null=True, blank=True, verbose_name="Fecha de Retiro"
    )

    is_repeat = models.BooleanField(default=False, verbose_name="Es repitente")

    class Meta:
        app_label = "students"
        verbose_name = "Matrícula"
        verbose_name_plural = "Matrículas"
        constraints = [
            UniqueConstraint(
                fields=["student", "section"], name="unique_student_section"
            ),
        ]
        indexes = [
            models.Index(fields=["student", "enrollment_status"]),
            models.Index(fields=["section", "enrollment_status"]),
        ]

    def __str__(self):
        return (
            f"{self.student} - {self.section} ({self.get_enrollment_status_display()})"
        )

    @property
    def school_year(self):
        return self.section.school_year
