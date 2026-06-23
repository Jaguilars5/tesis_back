from django.core.exceptions import ValidationError
from django.db import models
from apps.core.models import TimeStampedModel
from apps.integration.models.syncable_mixin import SyncableModel


class EvaluativeActivity(TimeStampedModel, SyncableModel):
    """
    ACTIVIDAD_EVALUATIVA — Tareas, lecciones, exámenes creados por el docente.
    Transaccional de alta frecuencia; creación continua durante el período.
    """

    block_component = models.ForeignKey(
        "grading.BlockComponent",
        on_delete=models.CASCADE,
        related_name="activities",
        verbose_name="Componente de Bloque",
    )
    teacher_subject_section = models.ForeignKey(
        "academic.TeacherSubjectSection",
        on_delete=models.CASCADE,
        related_name="evaluative_activities",
        verbose_name="Docente-Materia-Sección",
    )
    title = models.CharField(max_length=200, verbose_name="Título")
    activity_type = models.ForeignKey("grading.ActivityType", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Tipo de Actividad")
    max_score = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Puntuación Máxima"
    )
    due_date = models.DateField(verbose_name="Fecha de Vencimiento")
    internal_weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Ponderación Interna (%)",
        help_text="Peso de la actividad dentro de su componente",
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "grading"
        verbose_name = "Actividad Evaluativa"
        verbose_name_plural = "Actividades Evaluativas"
        ordering = ["-due_date"]
        indexes = [
            models.Index(fields=["teacher_subject_section", "due_date"]),
            models.Index(fields=["block_component", "due_date"]),
        ]

    def clean(self):
        super().clean()
        if self.block_component_id and self.teacher_subject_section_id:
            block = self.block_component.evaluation_block
            offering = block.subject_offering
            tss_offering = self.teacher_subject_section.subject_offering
            if offering.id != tss_offering.id:
                raise ValidationError(
                    {"teacher_subject_section": "El docente no está asignado a la oferta de esta actividad"}
                )
        if self.block_component_id and self.due_date:
            block = self.block_component.evaluation_block
            period = block.academic_period
            if self.due_date < period.start_date or self.due_date > period.end_date:
                raise ValidationError(
                    {"due_date": f"La fecha debe estar dentro del período académico ({period.start_date} - {period.end_date})"}
                )

    def __str__(self):
        return f"{self.title} ({self.activity_type})"
