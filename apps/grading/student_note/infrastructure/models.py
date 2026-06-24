from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, TextChoices

from apps.core.models import TimeStampedModel
from apps.integration.models.syncable_mixin import SyncableModel


class StudentNote(TimeStampedModel, SyncableModel):
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        verbose_name="Matr\u00edcula",
    )
    evaluative_activity = models.ForeignKey(
        "grading_evaluation.EvaluativeActivity",
        on_delete=models.CASCADE,
        verbose_name="Actividad Evaluativa",
    )
    grading_mode = models.CharField(
        max_length=20,
        choices=[("NUMERIC", "Cuantitativa"), ("QUALITATIVE", "Cualitativa")],
        default="NUMERIC",
        verbose_name="Modo de Calificaci\u00f3n",
    )
    qualitative_scale = models.ForeignKey(
        "grading_qualitative_scale.QualitativeScale",
        on_delete=models.PROTECT,
        null=True, blank=True,
        verbose_name="Escala Cualitativa",
    )
    numeric_score = models.DecimalField(
        max_digits=5, decimal_places=2,
        null=True, blank=True,
        verbose_name="Puntuaci\u00f3n Num\u00e9rica",
    )
    manually_overridden = models.BooleanField(default=False, verbose_name="Anulada Manualmente")
    teacher_observation = models.TextField(blank=True, default="", verbose_name="Observaci\u00f3n del Docente")
    created_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="student_notes_created", verbose_name="Creado por",
    )
    modified_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="student_notes_modified", verbose_name="Modificado por",
    )

    class Meta:
        app_label = "grading_student_note"
        verbose_name = "Nota de Actividad"
        verbose_name_plural = "Notas de Actividades"
        constraints = [
            models.UniqueConstraint(
                fields=["enrollment", "evaluative_activity"],
                condition=Q(evaluative_activity__isnull=False),
                name="unique_enrollment_activity",
            ),
        ]
        indexes = [
            models.Index(fields=["enrollment", "evaluative_activity"]),
            models.Index(fields=["evaluative_activity", "numeric_score"]),
            models.Index(fields=["sync_status"]),
            models.Index(fields=["enrollment", "sync_status"]),
        ]

    def clean(self):
        super().clean()
        if self.grading_mode == "NUMERIC" and not self.numeric_score:
            raise ValidationError({"numeric_score": "numeric_score es requerido para calificaci\u00f3n cuantitativa"})
        if self.grading_mode == "QUALITATIVE" and not self.qualitative_scale:
            raise ValidationError({"qualitative_scale": "qualitative_scale es requerido para calificaci\u00f3n cualitativa"})
        if self.evaluative_activity_id and self.numeric_score is not None:
            max_value = self.evaluative_activity.max_score
            if self.numeric_score < 0 or self.numeric_score > max_value:
                raise ValidationError({"numeric_score": f"La nota debe estar entre 0 y {max_value}"})
        if self.enrollment_id and self.evaluative_activity_id:
            activity_section_id = self.evaluative_activity.teacher_subject_section.subject_offering.section_id
            if self.enrollment.section_id != activity_section_id:
                raise ValidationError({"enrollment": "La matr\u00edcula no pertenece a la secci\u00f3n de la actividad evaluativa"})

    def calculate_normalized_value(self):
        if not self.evaluative_activity_id:
            return self.numeric_score
        max_value = Decimal(self.evaluative_activity.max_score)
        if max_value == 0:
            return Decimal("0.00")
        normalized = (Decimal(self.numeric_score) / max_value) * Decimal("10")
        return normalized.quantize(Decimal("0.01"))

    def __str__(self):
        return f"{self.enrollment} - {self.evaluative_activity} (score: {self.numeric_score})"


class GradeChangeHistory(TimeStampedModel):
    student_note = models.ForeignKey(
        "grading_student_note.StudentNote",
        on_delete=models.CASCADE,
        related_name="change_history",
        verbose_name="Nota",
    )
    modified_by_user = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True,
        verbose_name="Modificado por",
    )
    created_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="grade_changes_created", verbose_name="Creado por",
    )
    previous_score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Nota Anterior")
    new_score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Nota Nueva")
    previous_qualitative = models.ForeignKey(
        "grading_qualitative_scale.QualitativeScale",
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name="previous_grade_changes", verbose_name="Escala Cualitativa Anterior",
    )
    new_qualitative = models.ForeignKey(
        "grading_qualitative_scale.QualitativeScale",
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name="new_grade_changes", verbose_name="Nueva Escala Cualitativa",
    )
    reason = models.TextField(verbose_name="Raz\u00f3n del Cambio")
    reason_code = models.CharField(max_length=30, blank=True, verbose_name="C\u00f3digo de Raz\u00f3n")
    origin = models.CharField(
        max_length=20,
        choices=[("MANUAL", "Manual"), ("IMPORT", "Importaci\u00f3n"), ("SYNC", "Sincronizaci\u00f3n")],
        default="MANUAL", verbose_name="Origen",
    )
    device_origin = models.CharField(max_length=40, null=True, blank=True, verbose_name="Dispositivo de Origen")
    modified_at = models.DateTimeField(auto_now_add=True, verbose_name="Modificado en")

    class Meta:
        app_label = "grading_student_note"
        verbose_name = "Historial de Cambio de Calificaci\u00f3n"
        verbose_name_plural = "Historiales de Cambio de Calificaci\u00f3n"
        ordering = ["-modified_at"]
        indexes = [
            models.Index(fields=["student_note", "modified_at"]),
            models.Index(fields=["modified_by_user", "modified_at"]),
        ]

    def __str__(self):
        return f"{self.student_note} - {self.previous_score} \u2192 {self.new_score}"


class PromotionStatusChoices(TextChoices):
    APPROVED = "approved", "Aprobado"
    FAILED = "failed", "Reprobado"


class PeriodGradeSummary(TimeStampedModel):
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        related_name="grade_summaries",
        verbose_name="Matr\u00edcula",
    )
    subject_offering = models.ForeignKey(
        "academic_subject_offering.SubjectOffering",
        on_delete=models.CASCADE,
        related_name="grade_summaries",
        verbose_name="Oferta de Asignatura",
    )
    academic_period = models.ForeignKey(
        "academic_period.AcademicPeriod",
        on_delete=models.CASCADE,
        related_name="grade_summaries",
        verbose_name="Per\u00edodo Acad\u00e9mico",
    )
    formative_avg = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Promedio Formativo")
    summative_avg = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Promedio Sumativo")
    final_avg_truncated = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Promedio Final Truncado")
    qualitative_scale = models.ForeignKey(
        "grading_qualitative_scale.QualitativeScale",
        on_delete=models.PROTECT, null=True, blank=True,
        verbose_name="Escala Cualitativa",
    )
    is_failing = models.BooleanField(default=False, verbose_name="Est\u00e1 Reprobando")
    promotion_status = models.CharField(
        max_length=20, choices=PromotionStatusChoices.choices,
        null=True, blank=True, verbose_name="Estado de Promoci\u00f3n",
    )
    calculated_at = models.DateTimeField(auto_now_add=True, verbose_name="Calculado en")
    calculated_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="grade_summaries_calculated", verbose_name="Calculado por",
    )
    approved_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="grade_summaries_approved", verbose_name="Aprobado por",
    )

    class Meta:
        app_label = "grading_student_note"
        verbose_name = "Resumen de Calificaciones del Per\u00edodo"
        verbose_name_plural = "Res\u00famenes de Calificaciones del Per\u00edodo"
        constraints = [
            models.UniqueConstraint(
                fields=["enrollment", "subject_offering", "academic_period"],
                name="unique_period_grade_summary",
            ),
        ]
        indexes = [
            models.Index(fields=["academic_period", "subject_offering"]),
            models.Index(fields=["enrollment", "academic_period"]),
            models.Index(fields=["is_failing", "academic_period"]),
        ]

    def __str__(self):
        return f"{self.enrollment} - {self.subject_offering} ({self.academic_period})"
