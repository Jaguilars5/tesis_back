from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum, TextChoices

from apps.core.models import TimeStampedModel
from apps.integration.models.syncable_mixin import SyncableModel


class EvaluationBlockTypeChoices(TextChoices):
    FORMATIVA = "FORMATIVA", "Formativa"
    SUMATIVA = "SUMATIVA", "Sumativa"
    PROJECT = "PROJECT", "Proyecto"


class EvaluationBlock(TimeStampedModel):
    code = models.CharField(max_length=50, blank=True, db_index=True, verbose_name="C\u00f3digo")
    academic_period = models.ForeignKey(
        "academic_period.AcademicPeriod",
        on_delete=models.CASCADE,
        related_name="evaluation_blocks",
        verbose_name="Per\u00edodo Acad\u00e9mico",
    )
    subject_offering = models.ForeignKey(
        "academic_subject_offering.SubjectOffering",
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
        max_digits=5, decimal_places=2, verbose_name="Porcentaje de Ponderaci\u00f3n",
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "grading_evaluation"
        verbose_name = "Bloque de Evaluaci\u00f3n"
        verbose_name_plural = "Bloques de Evaluaci\u00f3n"
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
                    {"weight_percentage": f"La suma de pesos excede 100%. Actualmente: {total}%"}
                )

    def __str__(self):
        return f"{self.academic_period.name} \u2014 {self.name} ({self.get_block_type_display()})"


class BlockComponent(TimeStampedModel):
    code = models.CharField(max_length=50, blank=True, db_index=True, verbose_name="C\u00f3digo")
    evaluation_block = models.ForeignKey(
        "grading_evaluation.EvaluationBlock",
        on_delete=models.CASCADE,
        related_name="components",
        verbose_name="Bloque de Evaluaci\u00f3n",
    )
    name = models.CharField(max_length=100, verbose_name="Nombre")
    internal_weight = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Ponderaci\u00f3n Interna (%)",
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "grading_evaluation"
        verbose_name = "Componente de Bloque"
        verbose_name_plural = "Componentes de Bloque"
        ordering = ["evaluation_block", "name"]

    def clean(self):
        super().clean()
        if self.internal_weight and self.evaluation_block_id:
            total = BlockComponent.objects.filter(
                evaluation_block=self.evaluation_block,
                is_active=True,
            ).exclude(pk=self.pk).aggregate(total=Sum("internal_weight"))["total"] or 0
            if total + self.internal_weight > 100:
                raise ValidationError(
                    {"internal_weight": f"La suma de pesos internos excede 100%. Actualmente: {total}%"}
                )

    def __str__(self):
        return f"{self.evaluation_block.name} \u2014 {self.name}"


class EvaluativeActivity(TimeStampedModel, SyncableModel):
    block_component = models.ForeignKey(
        "grading_evaluation.BlockComponent",
        on_delete=models.CASCADE,
        related_name="activities",
        verbose_name="Componente de Bloque",
    )
    teacher_subject_section = models.ForeignKey(
        "academic_teacher_subject.TeacherSubjectSection",
        on_delete=models.CASCADE,
        related_name="evaluative_activities",
        verbose_name="Docente-Materia-Secci\u00f3n",
    )
    title = models.CharField(max_length=200, verbose_name="T\u00edtulo")
    activity_type = models.ForeignKey(
        "grading_activity_type.ActivityType",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Tipo de Actividad",
    )
    max_score = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Puntuaci\u00f3n M\u00e1xima"
    )
    due_date = models.DateField(verbose_name="Fecha de Vencimiento")
    internal_weight = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Ponderaci\u00f3n Interna (%)",
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "grading_evaluation"
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
                    {"teacher_subject_section": "El docente no est\u00e1 asignado a la oferta de esta actividad"}
                )
        if self.block_component_id and self.due_date:
            block = self.block_component.evaluation_block
            period = block.academic_period
            if self.due_date < period.start_date or self.due_date > period.end_date:
                raise ValidationError(
                    {"due_date": f"La fecha debe estar dentro del per\u00edodo acad\u00e9mico ({period.start_date} - {period.end_date})"}
                )

    def __str__(self):
        return f"{self.title} ({self.activity_type})"
