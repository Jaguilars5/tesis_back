from django.db import models
from apps.core.models import TimeStampedModel


class ClassSchedule(TimeStampedModel):
    subject_offering = models.ForeignKey(
        "academic.SubjectOffering",
        on_delete=models.CASCADE,
        related_name="schedules",
        verbose_name="Oferta de Materia",
    )
    day_of_week = models.ForeignKey(
        "academic.DayOfWeek",
        on_delete=models.PROTECT,
        verbose_name="Día de la Semana",
    )
    start_time = models.TimeField(verbose_name="Hora de inicio")
    end_time = models.TimeField(verbose_name="Hora de fin")
    classroom = models.CharField(max_length=50, blank=True, verbose_name="Aula")
    building = models.CharField(max_length=50, blank=True, verbose_name="Edificio")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "academic"
        verbose_name = "Horario Académico"
        verbose_name_plural = "Horarios Académicos"
        unique_together = [("subject_offering", "day_of_week", "start_time")]
        ordering = ["day_of_week", "start_time"]

    def __str__(self):
        return f"{self.subject_offering} - {self.day_of_week} ({self.start_time}-{self.end_time})"
