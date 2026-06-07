from django.db import models


class Enrollment(models.Model):
    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name="Estudiante",
    )
    section = models.ForeignKey(
        "institutions.Section",
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name="Sección",
    )
    school_year = models.ForeignKey(
        "institutions.School_Year",
        on_delete=models.CASCADE,
        verbose_name="Año Escolar",
    )
    enrollment_status = models.ForeignKey(
        "students.EnrollmentStatus",
        on_delete=models.PROTECT,
        verbose_name="Estado de Matrícula",
    )
    enrollment_date = models.DateField(
        verbose_name="Fecha de Matrícula",
        auto_now_add=True,
    )
    withdrawal_date = models.DateField(
        null=True, blank=True, verbose_name="Fecha de Retiro"
    )
    withdrawal_reason = models.TextField(
        blank=True, null=True, verbose_name="Motivo de Retiro"
    )
    is_repeat = models.BooleanField(default=False, verbose_name="Es repitente")
    repeated_school_year = models.ForeignKey(
        "institutions.School_Year",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="repeated_enrollments",
        verbose_name="Año escolar repetido",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de Actualización"
    )

    class Meta:
        app_label = "students"
        verbose_name = "Matrícula"
        verbose_name_plural = "Matrículas"
        unique_together = (("student", "section", "school_year"),)
        indexes = [
            models.Index(fields=["student", "enrollment_status"]),
            models.Index(fields=["section", "enrollment_status"]),
        ]

    def __str__(self):
        return f"{self.student} - {self.section} ({self.enrollment_status})"

    def save(self, *args, **kwargs):
        if not hasattr(self, "school_year") or self.school_year is None:
            if self.section and hasattr(self.section, "school_year") and self.section.school_year:
                self.school_year = self.section.school_year
        super().save(*args, **kwargs)
