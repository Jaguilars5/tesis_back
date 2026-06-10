from django.db import models
from apps.core.models import TimeStampedModel


class EnrollmentHistory(TimeStampedModel):
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        verbose_name="Matrícula",
    )
    previous_status = models.ForeignKey(
        "students.EnrollmentStatus",
        on_delete=models.PROTECT,
        related_name="previous_enrollments",
        verbose_name="Estado Anterior",
    )
    new_status = models.ForeignKey(
        "students.EnrollmentStatus",
        on_delete=models.PROTECT,
        related_name="new_enrollments",
        verbose_name="Nuevo Estado",
    )
    changed_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True,
        verbose_name="Cambiado por",
    )
    change_reason = models.TextField(blank=True, verbose_name="Razón del cambio")
    effective_date = models.DateField(verbose_name="Fecha efectiva")

    class Meta:
        app_label = "students"
        verbose_name = "Historial de Matrícula"
        verbose_name_plural = "Historiales de Matrícula"
        ordering = ["-effective_date"]

    def __str__(self):
        return f"{self.enrollment}: {self.previous_status} → {self.new_status} ({self.effective_date})"
