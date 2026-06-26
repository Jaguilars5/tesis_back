from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import TimeStampedModel
from apps.integration.models.syncable_mixin import SyncableModel


class Attendance(TimeStampedModel, SyncableModel):
    absence_type = models.ForeignKey(
        "attendance_absence_type.AbsenceType",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Tipo de ausencia",
    )
    attendance_status = models.ForeignKey(
        "attendance_attendance_status.AttendanceStatus",
        on_delete=models.PROTECT,
        verbose_name="Estado",
    )
    academic_period = models.ForeignKey(
        "academic_period.AcademicPeriod",
        on_delete=models.CASCADE,
        related_name="attendance_records",
        verbose_name="Per\u00edodo Academico",
    )
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        related_name="attendance_records",
        verbose_name="Matr\u00edcula",
    )
    teacher_subject_section = models.ForeignKey(
        "academic_teacher_subject.TeacherSubjectSection",
        on_delete=models.CASCADE,
        related_name="attendance_records",
        verbose_name="Clase",
    )
    class_schedule = models.ForeignKey(
        "academic_class_schedule.ClassSchedule",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Horario de clase",
    )

    is_active = models.BooleanField(default=True, verbose_name="Activo")
    attendance_date = models.DateField(verbose_name="Fecha")
    observation = models.TextField(blank=True, default="", verbose_name="Observaciones")

    class Meta:
        app_label = "attendance_core"
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
                        "teacher_subject_section": "La clase no pertenece a la secci\u00f3n de la matr\u00edcula"
                    }
                )
            if self.attendance_date:
                if (
                    self.attendance_date < self.academic_period.start_date
                    or self.attendance_date > self.academic_period.end_date
                ):
                    raise ValidationError(
                        {
                            "attendance_date": f"La fecha debe estar dentro del per\u00edodo academico ({self.academic_period.start_date} - {self.academic_period.end_date})"
                        }
                    )
        if self.class_schedule_id and self.teacher_subject_section_id:
            if self.class_schedule.teacher_subject_section_id != self.teacher_subject_section_id:
                raise ValidationError(
                    {
                        "class_schedule": "El horario no pertenece a la clase seleccionada"
                    }
                )
            cs_day = self.class_schedule.day_of_week
            date_day = self.attendance_date.isoweekday()
            if cs_day != date_day:
                import warnings
                warnings.warn(
                    f"La fecha ({self.attendance_date}, d\u00eda {date_day}) no coincide "
                    f"con el d\u00eda del horario ({cs_day})"
                )

    @property
    def absence_type_name(self):
        return self.absence_type.name if self.absence_type else None

    @property
    def attendance_status_name(self):
        return self.attendance_status.name if self.attendance_status else None

    @property
    def academic_period_name(self):
        return self.academic_period.name if self.academic_period else None

    @property
    def enrollment_name(self):
        return str(self.enrollment) if self.enrollment else None

    @property
    def teacher_subject_section_name(self):
        return str(self.teacher_subject_section) if self.teacher_subject_section else None

    @property
    def class_schedule_name(self):
        return str(self.class_schedule) if self.class_schedule else None

    def __str__(self):
        student = self.enrollment.student
        student_name = student.get_full_name() if student else "Sin estudiante"
        return f"{student_name} - {self.attendance_date} - {self.attendance_status}"
