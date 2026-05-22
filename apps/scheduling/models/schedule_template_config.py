from django.db import models


class ScheduleTemplateConfig(models.Model):
    """
    Configuración de la plantilla base para la generación de horarios.
    Define la duración de clases, recreos y la estructura diaria.

    day_start_time: Hora de inicio de la jornada
    class_duration_minutes: Duración de cada hora de clase
    break_duration_minutes: Duración del recreo
    slots_before_break: Cantidad de horas antes del recreo
    total_slots_per_day: Cantidad total de horas pedagógicas por día
    """

    day_start_time = models.TimeField(
        verbose_name="Hora de Inicio del Día",
        help_text="Hora de inicio de la jornada escolar",
    )
    class_duration_minutes = models.IntegerField(
        verbose_name="Duración de Clase (min)",
        help_text="Duración en minutos de cada clase",
    )
    break_duration_minutes = models.IntegerField(
        verbose_name="Duración del Recreo (min)",
        help_text="Duración en minutos del recreo",
    )
    slots_before_break = models.IntegerField(
        verbose_name="Periodos antes del Recreo",
        help_text="Número de periodos antes del primer recreo",
    )
    total_slots_per_day = models.IntegerField(
        verbose_name="Total de Periodos por Día",
        help_text="Total de periodos de clase por día",
    )

    class Meta:
        app_label = "scheduling"
        verbose_name = "Configuración de Plantilla de Horario"
        verbose_name_plural = "Configuraciones de Plantilla de Horarios"

    def __str__(self):
        return f"ScheduleTemplateConfig #{self.pk}"
