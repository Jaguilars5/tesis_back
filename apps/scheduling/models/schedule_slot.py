from django.db import models


class ScheduleSlot(models.Model):
    """
    Asignación final de una clase en el horario.

    teacher_subject_section: Relación docente-materia-sección asignada
    school_year: Año escolar vigente
    time_slot: Franja horaria asignada
    classroom: Aula donde se dictará la clase
    is_manual: Indica si la asignación fue manual o automática
    active: Indica si el slot está vigente
    """

    teacher_subject_section = models.ForeignKey(
        "academic.Teacher_Subject_Section",
        on_delete=models.CASCADE,
        verbose_name="Asignación Académica",
        help_text="Asignación académica",
    )
    school_year = models.ForeignKey(
        "institutions.School_Year",
        on_delete=models.CASCADE,
        verbose_name="Año Escolar",
        help_text="Año escolar",
    )
    time_slot = models.ForeignKey(
        "TimeSlot",
        on_delete=models.CASCADE,
        verbose_name="Franja Horaria",
        help_text="Franja horaria ocupada",
    )
    classroom = models.ForeignKey(
        "institutions.Classroom",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Aula",
        help_text="Aula asignada",
    )
    is_manual = models.BooleanField(
        default=True,
        verbose_name="Asignación Manual",
        help_text="Indica si fue asignado manualmente",
    )
    active = models.BooleanField(
        default=True, verbose_name="Activo", help_text="Indica si el slot está activo"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de Actualización"
    )

    class Meta:
        app_label = "scheduling"
        verbose_name = "Bloque de Horario"
        verbose_name_plural = "Bloques de Horario"
        unique_together = ("teacher_subject_section", "time_slot")

    def __str__(self):
        return f"{self.teacher_subject_section} - {self.time_slot}"
