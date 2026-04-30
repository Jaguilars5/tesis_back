from django.db import models

class ScheduleTemplateConfig(models.Model):
    """
    Configuración de la plantilla base para la generación de horarios.
    Define la duración de clases, recreos y la estructura diaria.

    timing_regime: Régimen horario (Matutino, Vespertino, etc.) al que aplica
    day_start_time: Hora de inicio de la jornada
    class_duration_minutes: Duración de cada hora de clase
    break_duration_minutes: Duración del recreo
    slots_before_break: Cantidad de horas antes del recreo
    total_slots_per_day: Cantidad total de horas pedagógicas por día
    """

    timing_regime = models.OneToOneField(
        "academic.Timing_Regime",
        on_delete=models.CASCADE,
        help_text="Régimen horario al que aplica esta configuración",
    )
    day_start_time = models.TimeField(help_text="Hora de inicio de la jornada escolar")
    class_duration_minutes = models.IntegerField(help_text="Duración en minutos de cada clase")
    break_duration_minutes = models.IntegerField(help_text="Duración en minutos del recreo")
    slots_before_break = models.IntegerField(
        help_text="Número de periodos antes del primer recreo"
    )
    total_slots_per_day = models.IntegerField(help_text="Total de periodos de clase por día")

    class Meta:
        app_label = "scheduling"

    def __str__(self):
        return f"Config for {self.timing_regime.name}"
