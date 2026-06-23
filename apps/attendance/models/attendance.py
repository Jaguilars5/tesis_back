from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from apps.core.models import TimeStampedModel
from apps.integration.models.syncable_mixin import SyncableModel


class Attendance(TimeStampedModel, SyncableModel):
    absence_type = models.ForeignKey(
        "attendance.AbsenceType",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Tipo de ausencia",
    )
    attendance_status = models.ForeignKey(
        "attendance.AttendanceStatus",
        on_delete=models.PROTECT,
        verbose_name="Estado",
    )
    academic_period = models.ForeignKey(
        "academic.AcademicPeriod",
        on_delete=models.CASCADE,
        related_name="attendance_records",
        verbose_name="Período Académico",
    )
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
    class_schedule = models.ForeignKey(
        "academic.ClassSchedule",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Horario de clase",
    )

    attendance_date = models.DateField(verbose_name="Fecha")
    observation = models.TextField(blank=True, default="", verbose_name="Observaciones")

    class Meta:
        app_label = "attendance"
        verbose_name = "Asistencia"
        verbose_name_plural = "Asistencias"
        constraints = [
            models.UniqueConstraint(
                fields=["enrollment", "teacher_subject_section", "attendance_date"],
                condition=models.Q(class_schedule__isnull=True),
                name="unique_attendance_no_schedule",
            ),
            models.UniqueConstraint(
                fields=["enrollment", "class_schedule", "attendance_date"],
                condition=models.Q(class_schedule__isnull=False),
                name="unique_attendance_with_schedule",
            ),
        ]
        indexes = [
            models.Index(fields=["enrollment", "academic_period"]),
            models.Index(fields=["teacher_subject_section", "attendance_date"]),
            models.Index(fields=["attendance_date", "academic_period"]),
            models.Index(fields=["class_schedule", "attendance_date"]),
        ]

    def clean(self):
        super().clean()
        if (
            self.enrollment_id
            and self.teacher_subject_section_id
            and self.academic_period_id
        ):
            tss_section = self.teacher_subject_section.subject_offering.section_id
            if self.enrollment.section_id != tss_section:
                raise ValidationError(
                    {
                        "teacher_subject_section": "La clase no pertenece a la sección de la matrícula"
                    }
                )
            if self.attendance_date:
                if (
                    self.attendance_date < self.academic_period.start_date
                    or self.attendance_date > self.academic_period.end_date
                ):
                    raise ValidationError(
                        {
                            "attendance_date": f"La fecha debe estar dentro del período académico ({self.academic_period.start_date} - {self.academic_period.end_date})"
                        }
                    )
        if self.class_schedule_id and self.teacher_subject_section_id:
            if self.class_schedule.teacher_subject_section_id != self.teacher_subject_section_id:
                raise ValidationError(
                    {
                        "class_schedule": "El horario no pertenece a la clase seleccionada"
                    }
                )
            # solo emite warning si el día no coincide (no bloquea)
            cs_day = self.class_schedule.day_of_week
            date_day = self.attendance_date.isoweekday()
            if cs_day != date_day:
                import warnings
                warnings.warn(
                    f"La fecha ({self.attendance_date}, día {date_day}) no coincide "
                    f"con el día del horario ({cs_day})"
                )

    def __str__(self):
        student = self.enrollment.student
        student_name = student.get_full_name() if student else "Sin estudiante"
        return f"{student_name} - {self.attendance_date} - {self.attendance_status}"
