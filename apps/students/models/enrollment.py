from django.db import models


class Enrollment(models.Model):
    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name="Estudiante",
    )
    section = models.ForeignKey(
        "academic.Section",
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name="Sección",
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

    # Sync fields
    sync_status = models.CharField(max_length=20, default="pending", verbose_name="Estado de Sincronización")
    synced_at = models.DateTimeField(null=True, blank=True, verbose_name="Sincronizado en")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Eliminación")
    sync_version = models.PositiveIntegerField(default=0, verbose_name="Versión de Sincronización")
    device_origin = models.CharField(max_length=40, null=True, blank=True, verbose_name="Dispositivo de Origen")

    class Meta:
        app_label = "students"
        verbose_name = "Matrícula"
        verbose_name_plural = "Matrículas"
        unique_together = ("student", "section")
        indexes = [
            models.Index(fields=["student", "enrollment_status"]),
            models.Index(fields=["section", "enrollment_status"]),
        ]

    def __str__(self):
        return f"{self.student} - {self.section} ({self.enrollment_status})"
