from django.db import models

class TimeSlot(models.Model):
    """
    Franja horaria específica dentro de un régimen horario.

    timing_regime: Régimen horario al que pertenece
    name: Nombre descriptivo (ej: '1ra Hora', 'Recreo')
    day_of_week: Día de la semana (1=Lunes, ..., 7=Domingo)
    start_time: Hora de inicio
    end_time: Hora de fin
    is_break: Indica si es un tiempo de recreo/descanso
    """

    timing_regime = models.ForeignKey(
        "academic.Timing_Regime",
        on_delete=models.CASCADE,
        help_text="Régimen horario que contiene este slot",
    )
    name = models.CharField(max_length=50, help_text="Nombre de la hora/periodo")
    day_of_week = models.IntegerField(help_text="Día de la semana (1-7)")
    start_time = models.TimeField(help_text="Hora de inicio del periodo")
    end_time = models.TimeField(help_text="Hora de fin del periodo")
    is_break = models.BooleanField(default=False, help_text="Indica si es tiempo de descanso")

    class Meta:
        app_label = "scheduling"

    def __str__(self):
        return f"{self.name} ({self.day_of_week})"
