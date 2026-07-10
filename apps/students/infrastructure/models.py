from django.db import models
from django.db.models import TextChoices, UniqueConstraint
from apps.core.models import TimeStampedModel
from apps.integration.infrastructure.models import SyncableModel


class EnrollmentStatusChoices(TextChoices):
    ACTIVE = "ACT", "Activa"
    WITHDRAWN = "RET", "Retirado"
    TRANSFERRED = "TRS", "Transferido"
    SUSPENDED = "SUS", "Suspendido"
    GRADUATED = "GRA", "Graduado"
    INACTIVE = "INA", "Inactivo"


class Student(TimeStampedModel):
    user = models.OneToOneField(
        "iam.User",
        on_delete=models.CASCADE,
        null=False,
        verbose_name="Usuario",
    )
    special_needs_type = models.ForeignKey(
        "students.SpecialNeedsType",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Tipo de NEE",
    )
    student_code = models.CharField(
        max_length=50, unique=True, verbose_name="Código de Estudiante"
    )
    has_special_needs = models.BooleanField(
        default=False, verbose_name="Tiene Necesidades Educativas Especiales (NEE)"
    )

    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "students"
        verbose_name = "Estudiante"
        verbose_name_plural = "Estudiantes"
        ordering = ["id"]
        indexes = [
            models.Index(fields=["student_code"]),
        ]

    def __str__(self):
        if self.user:
            return self.user.get_full_name()
        return f"Student #{self.pk}"

    def get_full_name(self):
        if self.user:
            return self.user.get_full_name()
        return ""

    def get_age(self):
        from datetime import date

        if self.user and self.user.birth_date:
            today = date.today()
            return (
                today.year
                - self.user.birth_date.year
                - (
                    (today.month, today.day)
                    < (self.user.birth_date.month, self.user.birth_date.day)
                )
            )
        return 0


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


class WithdrawalReason(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "students"
        verbose_name = "Motivo de Retiro"
        verbose_name_plural = "Motivos de Retiro"
        ordering = ["name"]

    def __str__(self):
        return self.name


class SpecialNeedsType(models.Model):
    code = models.CharField(max_length=30, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "students"
        verbose_name = "Tipo de Necesidad Especial"
        verbose_name_plural = "Tipos de Necesidades Especiales"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Kinship(models.Model):
    code = models.CharField(max_length=30, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "students"
        verbose_name = "Parentesco"
        verbose_name_plural = "Parentescos"
        ordering = ["name"]

    def __str__(self):
        return self.name
