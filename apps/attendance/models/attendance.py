import uuid
from django.db import models
from apps.core.models import TimeStampedModel


class Attendance(TimeStampedModel):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="UUID")
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        related_name="attendance_records",
        verbose_name="Matrícula",
        null=True,
    )
    teacher_subject_section = models.ForeignKey(
        "academic.TeacherSubjectSection",
        on_delete=models.CASCADE,
        related_name="attendance_records",
        verbose_name="Clase",
    )
    academic_period = models.ForeignKey(
        "academic.AcademicPeriod",
        on_delete=models.CASCADE,
        related_name="attendance_records",
        verbose_name="Período Académico",
    )
    attendance_status = models.ForeignKey(
        "attendance.AttendanceStatus",
        on_delete=models.PROTECT,
        verbose_name="Estado",
        null=True,
    )
    attendance_date = models.DateField(verbose_name="Fecha", null=True)
    absence_type = models.ForeignKey("attendance.AbsenceType", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Tipo de ausencia")
    observation = models.TextField(null=True, blank=True, verbose_name="Observaciones")
    sync_status = models.CharField(max_length=20, default="pending", verbose_name="Estado de Sincronización")
    synced_at = models.DateTimeField(null=True, blank=True, verbose_name="Sincronizado en")
    sync_version = models.PositiveIntegerField(default=0, verbose_name="Versión de Sincronización")
    device_origin = models.CharField(max_length=40, null=True, blank=True, verbose_name="Dispositivo de Origen")

    class Meta:
        app_label = "attendance"
        verbose_name = "Asistencia"
        verbose_name_plural = "Asistencias"
        unique_together = ("enrollment", "teacher_subject_section", "attendance_date")
        indexes = [
            models.Index(fields=["enrollment", "academic_period"]),
            models.Index(fields=["teacher_subject_section", "attendance_date"]),
        ]

    def __str__(self):
        return f"{self.enrollment} - {self.attendance_date} - {self.attendance_status}"
