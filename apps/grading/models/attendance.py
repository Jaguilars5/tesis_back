from django.db import models
import uuid


class Attendance(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="UUID")
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        verbose_name="Matrícula",
        null=True,
    )
    teacher_subject_section = models.ForeignKey(
        "academic.Teacher_Subject_Section",
        on_delete=models.CASCADE,
        verbose_name="Clase",
    )
    academic_period = models.ForeignKey(
        "academic.Academic_Period",
        on_delete=models.CASCADE,
        verbose_name="Período Académico",
    )
    attendance_status = models.ForeignKey(
        "grading.AttendanceStatus",
        on_delete=models.PROTECT,
        verbose_name="Estado",
        null=True,
    )
    attendance_date = models.DateField(verbose_name="Fecha", null=True)
    observation = models.TextField(null=True, blank=True, verbose_name="Observaciones")

    sync_status = models.CharField(max_length=20, default="pending", verbose_name="Estado de Sincronización")
    synced_at = models.DateTimeField(null=True, blank=True, verbose_name="Sincronizado en")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
    sync_version = models.PositiveIntegerField(default=0, verbose_name="Versión de Sincronización")
    device_origin = models.CharField(max_length=40, null=True, blank=True, verbose_name="Dispositivo de Origen")

    class Meta:
        app_label = "grading"
        verbose_name = "Asistencia"
        verbose_name_plural = "Asistencias"
        unique_together = ("enrollment", "teacher_subject_section", "attendance_date")
        indexes = [
            models.Index(fields=["enrollment", "academic_period"]),
            models.Index(fields=["teacher_subject_section", "attendance_date"]),
        ]

    def __str__(self):
        return f"{self.enrollment} - {self.attendance_date} - {self.attendance_status}"
