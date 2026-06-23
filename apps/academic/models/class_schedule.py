from django.db import models
from apps.core.models import TimeStampedModel

"""Deprecated: No lo elimino hasta no tener claro que no se usa en ningún lado, pero lo más probable es que se elimine en el futuro."""


class DayOfWeekChoices(models.IntegerChoices):
    """Enumeración de días de la semana."""

    MONDAY = 1, "Lunes"
    TUESDAY = 2, "Martes"
    WEDNESDAY = 3, "Miércoles"
    THURSDAY = 4, "Jueves"
    FRIDAY = 5, "Viernes"
    SATURDAY = 6, "Sábado"
    SUNDAY = 7, "Domingo"


class ClassSchedule(TimeStampedModel):
    """Define el horario de clases para una asignación docente-materia-sección."""

    teacher_subject_section = models.ForeignKey(
        "academic.TeacherSubjectSection",
        on_delete=models.CASCADE,
        related_name="schedules",
        verbose_name="Asignación Docente-Materia-Sección",
    )
    day_of_week = models.IntegerField(
        choices=DayOfWeekChoices.choices,
        verbose_name="Día de la Semana",
    )
    start_time = models.TimeField(verbose_name="Hora de inicio")
    end_time = models.TimeField(verbose_name="Hora de fin")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "academic"
        verbose_name = "Horario Académico"
        verbose_name_plural = "Horarios Académicos"
        constraints = [
            models.UniqueConstraint(
                fields=["teacher_subject_section", "day_of_week", "start_time"],
                name="unique_class_schedule",
            ),
        ]
        ordering = ["day_of_week", "start_time"]

    def __str__(self):
        return f"{self.teacher_subject_section} - {self.get_day_of_week_display()} ({self.start_time}-{self.end_time})"
