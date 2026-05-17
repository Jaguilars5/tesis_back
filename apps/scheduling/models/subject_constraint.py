from django.db import models


class SubjectConstraint(models.Model):
    subject_academic_config = models.ForeignKey(
        "academic.SubjectAcademicConfig",
        on_delete=models.CASCADE,
        verbose_name="Configuración de Materia",
        null=True,
    )
    required_consecutive_slots = models.IntegerField(
        default=1,
        verbose_name="Periodos Consecutivos Requeridos",
        help_text="Número de periodos seguidos requeridos",
    )
    max_slots_per_day = models.IntegerField(
        default=2,
        verbose_name="Máximo de Periodos por Día",
        help_text="Máximo de periodos permitidos por día",
    )
    preferred_room_type = models.ForeignKey(
        "institutions.RoomType",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Tipo de Aula Preferida",
        help_text="Preferencia de tipo de aula",
    )

    class Meta:
        app_label = "scheduling"
        verbose_name = "Restricción de Materia"
        verbose_name_plural = "Restricciones de Materias"

    def __str__(self):
        return f"Constraint for {self.subject_academic_config}"
