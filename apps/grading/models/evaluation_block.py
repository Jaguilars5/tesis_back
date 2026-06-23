from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import TextChoices, Sum
from apps.core.models import TimeStampedModel


class EvaluationBlockTypeChoices(TextChoices):
    FORMATIVA = "FORMATIVA", "Formativa"
    SUMATIVA = "SUMATIVA", "Sumativa"
    PROJECT = "PROJECT", "Proyecto"


class EvaluationBlock(TimeStampedModel):
    """
    BLOQUE_EVALUACION — Bloques formativo/sumativo/diagnóstico por período académico.
    Se configura al inicio de cada período.
    """

    code = models.CharField(max_length=50, blank=True, db_index=True, verbose_name="Código")
    academic_period = models.ForeignKey(
        "academic.AcademicPeriod",
        on_delete=models.CASCADE,
        related_name="evaluation_blocks",
        verbose_name="Período Académico",
    )
    subject_offering = models.ForeignKey(
        "academic.SubjectOffering",
        on_delete=models.CASCADE,
        related_name="evaluation_blocks",
        verbose_name="Oferta de Materia",
    )
    name = models.CharField(max_length=100, verbose_name="Nombre")
    block_type = models.CharField(
        max_length=20, choices=EvaluationBlockTypeChoices.choices,
        null=True, blank=True, verbose_name="Tipo de bloque",
    )
    weight_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Porcentaje de Ponderación",
        help_text="Porcentaje que representa este bloque en la nota final del período",
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "grading"
        verbose_name = "Bloque de Evaluación"
        verbose_name_plural = "Bloques de Evaluación"
        ordering = ["academic_period", "subject_offering", "block_type"]
        indexes = [
            models.Index(fields=["subject_offering", "academic_period"]),
        ]

    def clean(self):
        super().clean()
        if self.weight_percentage and self.subject_offering_id and self.academic_period_id:
            total = EvaluationBlock.objects.filter(
                subject_offering=self.subject_offering,
                academic_period=self.academic_period,
                is_active=True,
            ).exclude(pk=self.pk).aggregate(total=Sum("weight_percentage"))["total"] or 0
            if total + self.weight_percentage > 100:
                raise ValidationError(
                    {"weight_percentage": f"La suma de pesos excede 100%. Actualmente: {total}%, intentando agregar: {self.weight_percentage}%"}
                )

    def __str__(self):
        return f"{self.academic_period.name} — {self.name} ({self.get_block_type_display()})"