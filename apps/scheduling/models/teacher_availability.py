from django.db import models

class TeacherAvailability(models.Model):
    """
    Disponibilidad de un docente en una franja horaria y año escolar específicos.

    user: Usuario (docente)
    school_year: Año escolar de la disponibilidad
    time_slot: Franja horaria evaluada
    is_available: Indica si el docente está disponible en ese horario
    """

    user = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, help_text="Docente"
    )
    school_year = models.ForeignKey(
        "institutions.School_Year",
        on_delete=models.CASCADE,
        help_text="Año escolar",
    )
    time_slot = models.ForeignKey(
        "TimeSlot", on_delete=models.CASCADE, help_text="Franja horaria"
    )
    is_available = models.BooleanField(
        default=True, help_text="Indica disponibilidad del docente"
    )

    class Meta:
        app_label = "scheduling"

    def __str__(self):
        return f"{self.user} - {self.time_slot} ({self.is_available})"
