from django.db import models
from apps.core.models import TimeStampedModel
from apps.integration.models.syncable_mixin import SyncableModel


class SkillEvaluation(TimeStampedModel, SyncableModel):
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        related_name="skill_evaluations",
        verbose_name="Matrícula",
    )
    academic_period = models.ForeignKey(
        "academic.AcademicPeriod",
        on_delete=models.CASCADE,
        related_name="skill_evaluations",
        verbose_name="Período Académico",
    )
    socioemotional_skill = models.ForeignKey(
        "behavior.SocioemotionalSkill",
        on_delete=models.CASCADE,
        related_name="evaluations",
        verbose_name="Habilidad",
    )
    qualitative_scale = models.ForeignKey(
        "grading.QualitativeScale",
        on_delete=models.PROTECT,
        verbose_name="Escala Cualitativa",
    )
    observation = models.TextField(null=True, blank=True, verbose_name="Observación")
    evaluation_date = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Evaluación")

    class Meta:
        app_label = "behavior"
        verbose_name = "Evaluación de Habilidad"
        verbose_name_plural = "Evaluaciones de Habilidades"
        unique_together = ("enrollment", "academic_period", "socioemotional_skill")
        indexes = [
            models.Index(fields=["academic_period", "socioemotional_skill"]),
        ]

    def __str__(self):
        return f"{self.enrollment} - {self.socioemotional_skill.name}"
