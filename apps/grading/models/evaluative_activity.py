from django.db import models
from apps.core.models import TimeStampedModel
from apps.integration.models.syncable_mixin import SyncableModel


class EvaluativeActivity(TimeStampedModel, SyncableModel):
    """
    ACTIVIDAD_EVALUATIVA — Tareas, lecciones, exámenes creados por el docente.
    Transaccional de alta frecuencia; creación continua durante el período.
    """

    component_indicator = models.ForeignKey(
        "grading.ComponentIndicator",
        on_delete=models.CASCADE,
        related_name="activities",
        verbose_name="Indicador de Componente",
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
    is_interdisciplinary_project = models.BooleanField(
        default=False,
        verbose_name="Es Proyecto Interdisciplinar",
        help_text="Indica si esta actividad forma parte de un proyecto interdisciplinar",
    )

    class Meta:
        app_label = "grading"
        verbose_name = "Actividad Evaluativa"
        verbose_name_plural = "Actividades Evaluativas"
        ordering = ["-due_date"]
        indexes = [
            models.Index(fields=["teacher_subject_section", "due_date"]),
            models.Index(fields=["component_indicator", "due_date"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.activity_type})"
