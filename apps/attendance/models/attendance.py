from django.db import models
from apps.core.models import TimeStampedModel
from apps.integration.models.syncable_mixin import SyncableModel


class Attendance(TimeStampedModel, SyncableModel):
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        related_name="attendance_records",
        verbose_name="Matrícula",
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
    created_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="attendances_created", verbose_name="Creado por",
    )
    modified_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="attendances_modified", verbose_name="Modificado por",
    )

    class Meta:
        app_label = "attendance"
        verbose_name = "Asistencia"
        verbose_name_plural = "Asistencias"
        unique_together = ("enrollment", "teacher_subject_section", "attendance_date")
        indexes = [
            models.Index(fields=["enrollment", "academic_period"]),
            models.Index(fields=["teacher_subject_section", "attendance_date"]),
            models.Index(fields=["attendance_date", "academic_period"]),
        ]

    def __str__(self):
        return f"{self.enrollment} - {self.attendance_date} - {self.attendance_status}"
