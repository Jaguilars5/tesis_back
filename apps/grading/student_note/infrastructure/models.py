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
        verbose_name="Matricula",
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
        verbose_name="Modo de Calificacion",
    )
    qualitative_scale = models.ForeignKey(
        "grading_qualitative_scale.QualitativeScale",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Escala Cualitativa",
    )
    numeric_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Puntuacion Numerica",
    )
    manually_overridden = models.BooleanField(
        default=False, verbose_name="Anulada Manualmente"
    )
    teacher_observation = models.TextField(
        blank=True, default="", verbose_name="Observacion del Docente"
    )
    created_by = models.ForeignKey(
        "iam.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_notes_created",
        verbose_name="Creado por",
    )
    modified_by = models.ForeignKey(
        "iam.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_notes_modified",
        verbose_name="Modificado por",
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
            raise ValidationError(
                {
                    "numeric_score": "numeric_score es requerido para calificacion cuantitativa"
                }
            )
        if self.grading_mode == "QUALITATIVE" and not self.qualitative_scale:
            raise ValidationError(
                {
                    "qualitative_scale": "qualitative_scale es requerido para calificacion cualitativa"
                }
            )
        if self.evaluative_activity_id and self.numeric_score is not None:
            max_value = self.evaluative_activity.max_score
            if self.numeric_score < 0 or self.numeric_score > max_value:
                raise ValidationError(
                    {"numeric_score": f"La nota debe estar entre 0 y {max_value}"}
                )
        if self.enrollment_id and self.evaluative_activity_id:
            activity_section_id = (
                self.evaluative_activity.teacher_subject_section.subject_offering.section_id
            )
            if self.enrollment.section_id != activity_section_id:
                raise ValidationError(
                    {
                        "enrollment": "La matricula no pertenece a la seccion de la actividad evaluativa"
                    }
                )

    def calculate_normalized_value(self):
        if not self.evaluative_activity_id:
            return self.numeric_score
        max_value = Decimal(self.evaluative_activity.max_score)
        if max_value == 0:
            return Decimal("0.00")
        normalized = (Decimal(self.numeric_score) / max_value) * Decimal("10")
        return normalized.quantize(Decimal("0.01"))

    @property
    def enrollment_name(self):
        return str(self.enrollment) if self.enrollment else None

    @property
    def evaluative_activity_title(self):
        return self.evaluative_activity.title if self.evaluative_activity else None

    @property
    def qualitative_scale_name(self):
        return self.qualitative_scale.name if self.qualitative_scale else None

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
        "iam.User",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Modificado por",
    )
    created_by = models.ForeignKey(
        "iam.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="grade_changes_created",
        verbose_name="Creado por",
    )
    previous_score = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Nota Anterior"
    )
    new_score = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Nota Nueva"
    )
    previous_qualitative = models.ForeignKey(
        "grading_qualitative_scale.QualitativeScale",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="previous_grade_changes",
        verbose_name="Escala Cualitativa Anterior",
    )
    new_qualitative = models.ForeignKey(
        "grading_qualitative_scale.QualitativeScale",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="new_grade_changes",
        verbose_name="Nueva Escala Cualitativa",
    )
    reason = models.TextField(verbose_name="Razon del Cambio")
    reason_code = models.CharField(
        max_length=30, blank=True, verbose_name="Codigo de Razon"
    )
    origin = models.CharField(
        max_length=20,
        choices=[
            ("MANUAL", "Manual"),
            ("IMPORT", "Importacion"),
            ("SYNC", "Sincronizacion"),
        ],
        default="MANUAL",
        verbose_name="Origen",
    )
    device_origin = models.CharField(
        max_length=40, null=True, blank=True, verbose_name="Dispositivo de Origen"
    )
    modified_at = models.DateTimeField(auto_now_add=True, verbose_name="Modificado en")

    class Meta:
        app_label = "grading_student_note"
        verbose_name = "Historial de Cambio de Calificacion"
        verbose_name_plural = "Historiales de Cambio de Calificacion"
        ordering = ["-modified_at"]
        indexes = [
            models.Index(fields=["student_note", "modified_at"]),
            models.Index(fields=["modified_by_user", "modified_at"]),
        ]

    @property
    def student_note_name(self):
        return str(self.student_note) if self.student_note else None

    @property
    def modified_by_user_name(self):
        if self.modified_by_user and hasattr(self.modified_by_user, "person"):
            return self.modified_by_user.person.get_full_name()
        return None

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
        verbose_name="Matricula",
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
        verbose_name="Periodo Academico",
    )
    formative_avg = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Promedio Formativo"
    )
    summative_avg = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Promedio Sumativo"
    )
    final_avg_truncated = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Promedio Final Truncado"
    )
    qualitative_scale = models.ForeignKey(
        "grading_qualitative_scale.QualitativeScale",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Escala Cualitativa",
    )
    is_failing = models.BooleanField(default=False, verbose_name="Esta Reprobando")
    promotion_status = models.CharField(
        max_length=20,
        choices=PromotionStatusChoices.choices,
        null=True,
        blank=True,
        verbose_name="Estado de Promocion",
    )
    calculated_at = models.DateTimeField(auto_now_add=True, verbose_name="Calculado en")
    calculated_by = models.ForeignKey(
        "iam.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="grade_summaries_calculated",
        verbose_name="Calculado por",
    )
    approved_by = models.ForeignKey(
        "iam.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="grade_summaries_approved",
        verbose_name="Aprobado por",
    )

    class Meta:
        app_label = "grading_student_note"
        verbose_name = "Resumen de Calificaciones del Periodo"
        verbose_name_plural = "Res\u00famenes de Calificaciones del Periodo"
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

    @property
    def enrollment_name(self):
        return str(self.enrollment) if self.enrollment else None

    @property
    def subject_offering_name(self):
        return str(self.subject_offering) if self.subject_offering else None

    @property
    def academic_period_name(self):
        return self.academic_period.name if self.academic_period else None

    @property
    def qualitative_scale_name(self):
        return self.qualitative_scale.name if self.qualitative_scale else None

    def __str__(self):
        return f"{self.enrollment} - {self.subject_offering} ({self.academic_period})"


class AnnualGradeSummary(TimeStampedModel):
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        related_name="annual_grade_summaries",
        verbose_name="Matricula",
    )
    subject_offering = models.ForeignKey(
        "academic_subject_offering.SubjectOffering",
        on_delete=models.CASCADE,
        related_name="annual_grade_summaries",
        verbose_name="Oferta de Asignatura",
    )
    school_year = models.ForeignKey(
        "institutions_school_year.SchoolYear",
        on_delete=models.CASCADE,
        related_name="annual_grade_summaries",
        verbose_name="Año Escolar",
    )
    annual_final_avg = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Promedio Final Anual",
    )
    is_failing = models.BooleanField(
        default=False,
        verbose_name="Reprob\u00f3 la materia",
    )
    promotion_status = models.CharField(
        max_length=20,
        choices=PromotionStatusChoices.choices,
        null=True,
        blank=True,
        verbose_name="Estado de Promoci\u00f3n",
    )
    is_finalized = models.BooleanField(
        default=False,
        verbose_name="Resultado Anual Definitivo",
    )
    calculated_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Calculado en",
    )
    calculated_by = models.ForeignKey(
        "iam.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="annual_grade_summaries_calculated",
        verbose_name="Calculado por",
    )
    approved_by = models.ForeignKey(
        "iam.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="annual_grade_summaries_approved",
        verbose_name="Aprobado por",
    )

    class Meta:
        app_label = "grading_student_note"
        verbose_name = "Resumen Anual de Calificaciones"
        verbose_name_plural = "Res\u00famenes Anuales de Calificaciones"
        constraints = [
            models.UniqueConstraint(
                fields=["enrollment", "subject_offering", "school_year"],
                name="unique_annual_grade_summary",
            ),
        ]
        indexes = [
            models.Index(fields=["school_year", "subject_offering"]),
            models.Index(fields=["enrollment", "school_year"]),
            models.Index(fields=["is_failing", "school_year"]),
        ]

    @property
    def enrollment_name(self):
        return str(self.enrollment) if self.enrollment else None

    @property
    def subject_offering_name(self):
        return str(self.subject_offering) if self.subject_offering else None

    @property
    def school_year_name(self):
        return str(self.school_year) if self.school_year else None

    def __str__(self):
        return f"{self.enrollment} - {self.subject_offering} ({self.school_year})"
