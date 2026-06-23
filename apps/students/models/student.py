from django.db import models
from apps.core.models import TimeStampedModel


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
