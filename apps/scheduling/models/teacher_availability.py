from django.db import models


class TeacherAvailability(models.Model):
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        verbose_name="Docente",
    )
    time_slot = models.ForeignKey(
        "TimeSlot",
        on_delete=models.CASCADE,
        verbose_name="Franja Horaria",
    )
    is_available = models.BooleanField(
        default=True,
        verbose_name="Está Disponible",
    )

    class Meta:
        app_label = "scheduling"
        verbose_name = "Disponibilidad del Docente"
        verbose_name_plural = "Disponibilidades de los Docentes"

    def __str__(self):
        return f"{self.user} - {self.time_slot} ({self.is_available})"
