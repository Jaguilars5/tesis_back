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
        help_text="Asignación académica",
    )
    school_year = models.ForeignKey(
        "institutions.School_Year",
        on_delete=models.CASCADE,
        help_text="Año escolar",
    )
    time_slot = models.ForeignKey(
        "TimeSlot", on_delete=models.CASCADE, help_text="Franja horaria ocupada"
    )
    classroom = models.ForeignKey(
        "institutions.Classroom",
        on_delete=models.SET_NULL,
        null=True,
        help_text="Aula asignada",
    )
    is_manual = models.BooleanField(
        default=True, help_text="Indica si fue asignado manualmente"
    )
    active = models.BooleanField(default=True, help_text="Indica si el slot está activo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "scheduling"
        unique_together = ("teacher_subject_section", "time_slot")

    def __str__(self):
        return f"{self.teacher_subject_section} - {self.time_slot}"
