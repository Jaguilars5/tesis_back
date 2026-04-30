from django.db import models

class SubjectConstraint(models.Model):
    """
    Restricciones de planificación para una materia.

    subject: Materia a la que aplica la restricción
    required_consecutive_slots: Cantidad de horas seguidas requeridas (bloques)
    max_slots_per_day: Cantidad máxima de horas permitidas por día
    preferred_room_type: Tipo de aula preferida (ej: 'Laboratorio')
    """

    subject = models.ForeignKey(
        "academic.Subject",
        on_delete=models.CASCADE,
        help_text="Materia restringida",
    )
    required_consecutive_slots = models.IntegerField(
        default=1, help_text="Número de periodos seguidos requeridos"
    )
    max_slots_per_day = models.IntegerField(
        default=2, help_text="Máximo de periodos permitidos por día"
    )
    preferred_room_type = models.CharField(
        max_length=50, null=True, blank=True, help_text="Preferencia de tipo de aula"
    )

    class Meta:
        app_label = "scheduling"

    def __str__(self):
        return f"Constraint for {self.subject}"
