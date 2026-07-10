import logging
from decimal import Decimal

from django.db import transaction

from ..application import validators

logger = logging.getLogger(__name__)


def _enqueue_activity_graded_notification(note):
    """Programa la notificación de actividad calificada al confirmar la transacción."""
    if not note or not getattr(note, "id", None):
        return
    try:
        from apps.core.notifications.tasks import notify_activity_graded

        transaction.on_commit(lambda: notify_activity_graded.delay(note.id))
    except Exception:
        logger.warning(
            "No se pudo programar la notificación de calificación note=%s",
            getattr(note, "id", None),
            exc_info=True,
        )


from ..infrastructure.repositories import (
    StudentNoteRepository,
    PeriodGradeSummaryRepository,
    AnnualGradeSummaryRepository,
    EvaluationRepository,
)


def _load_evaluative_activity(evaluative_activity_id):
    from apps.grading.evaluation.infrastructure.models import EvaluativeActivity

    return (
        EvaluativeActivity.objects.select_related(
            "block_component__evaluation_block__academic_period",
        )
        .filter(pk=evaluative_activity_id)
        .first()
    )


def _record_grade_change(existing, note, user_id=None, device_origin=None, reason=""):
    from ..infrastructure.models import GradeChangeHistory

    if not validators.is_score_changing(
        existing,
        note.numeric_score,
        note.qualitative_scale_id,
    ):
        return

    GradeChangeHistory.objects.create(
        student_note=note,
        modified_by_user_id=user_id,
        previous_score=existing.numeric_score if existing.numeric_score is not None else Decimal("0.00"),
        new_score=note.numeric_score if note.numeric_score is not None else Decimal("0.00"),
        previous_qualitative=existing.qualitative_scale,
        new_qualitative=note.qualitative_scale,
        reason=reason or "Actualización de calificación",
        reason_code="UPDATE",
        origin="SYNC" if device_origin else "MANUAL",
        device_origin=device_origin,
    )


class StudentNoteService:
    """Logica de negocio para notas de estudiantes."""

    repository = StudentNoteRepository

    @classmethod
    @transaction.atomic
    def create_student_note(
        cls,
        enrollment_id,
        evaluative_activity_id,
        numeric_score,
        qualitative_scale_id=None,
        teacher_observation="",
        device_origin=None,
        user_id=None,
        change_reason="",
    ):
        activity = _load_evaluative_activity(evaluative_activity_id)
        if not activity:
            raise ValueError({"evaluative_activity_id": "Actividad evaluativa no encontrada"})

        existing = cls.repository.get_by_composite_key(
            enrollment_id, evaluative_activity_id,
        )
        score_changing = validators.is_score_changing(
            existing, numeric_score, qualitative_scale_id,
        )

        errors = validators.run_all_validators(
            enrollment_id=enrollment_id,
            evaluative_activity_id=evaluative_activity_id,
            numeric_score=numeric_score,
            evaluative_activity=activity,
            existing_note=existing,
            is_score_change=score_changing,
        )
        if errors:
            raise ValueError(errors)

        if existing:
            previous = cls.repository.get_by_id(existing.id)
            note = cls.repository.update(
                existing.id,
                numeric_score=numeric_score,
                teacher_observation=teacher_observation,
                qualitative_scale_id=qualitative_scale_id,
                device_origin=device_origin,
            )
            note = cls.repository.get_by_id(note.id)
            note.full_clean()
            if score_changing:
                _record_grade_change(
                    previous, note, user_id=user_id,
                    device_origin=device_origin, reason=change_reason,
                )
        else:
            note = cls.repository.create(
                enrollment_id=enrollment_id,
                evaluative_activity_id=evaluative_activity_id,
                numeric_score=numeric_score,
                qualitative_scale_id=qualitative_scale_id,
                teacher_observation=teacher_observation,
            )
            note.full_clean()

        _enqueue_activity_graded_notification(note)
        return note

    @classmethod
    def get_student_note(cls, note_id):
        note = cls.repository.get_by_id(note_id)
        if not note:
            raise ValueError(f"Calificacion {note_id} no encontrada")
        return note

    @classmethod
    def list_student_notes(cls, student_id=None, academic_period_id=None, subject_id=None, section_id=None):
        return cls.repository.list_by_filters(
            student_id=student_id,
            academic_period_id=academic_period_id,
            subject_id=subject_id,
            section_id=section_id,
        )

    @classmethod
    def update_student_note(cls, note_id, user_id=None, change_reason="", device_origin=None, **kwargs):
        note = cls.get_student_note(note_id)
        activity = _load_evaluative_activity(note.evaluative_activity_id)
        if not activity:
            raise ValueError({"evaluative_activity_id": "Actividad evaluativa no encontrada"})

        new_numeric = kwargs.get("numeric_score", note.numeric_score)
        new_qualitative_id = kwargs.get("qualitative_scale_id", note.qualitative_scale_id)
        score_changing = validators.is_score_changing(
            note, new_numeric, new_qualitative_id,
        )

        errors = validators.run_all_validators(
            enrollment_id=note.enrollment_id,
            evaluative_activity_id=note.evaluative_activity_id,
            numeric_score=new_numeric,
            evaluative_activity=activity,
            existing_note=note,
            is_score_change=score_changing,
        )
        if errors:
            raise ValueError(errors)

        allowed = {
            "numeric_score", "qualitative_scale_id", "teacher_observation",
            "manually_overridden", "grading_mode", "device_origin",
        }
        clean = {k: v for k, v in kwargs.items() if k in allowed}
        previous = cls.repository.get_by_id(note_id)
        updated = cls.repository.update(note_id, **clean)
        updated = cls.repository.get_by_id(note_id)
        updated.full_clean()
        if score_changing:
            _record_grade_change(
                previous, updated, user_id=user_id,
                device_origin=device_origin or clean.get("device_origin"),
                reason=change_reason,
            )
        _enqueue_activity_graded_notification(updated)
        return updated

    @classmethod
    def calculate_period_average(cls, student_id, academic_period_id=None, subject_id=None, section_id=None):
        queryset = cls.repository.list_by_filters(
            student_id=student_id,
            academic_period_id=academic_period_id,
            subject_id=subject_id,
            section_id=section_id,
        )
        notes = list(queryset)
        if not notes:
            return None

        total = Decimal("0.00")
        for note in notes:
            total += note.calculate_normalized_value()

        avg = total / Decimal(len(notes))
        return avg.quantize(Decimal("0.01"))

    @classmethod
    @transaction.atomic
    def anular_nota(cls, note_id, user_id, reason=""):
        """
        Anula una nota marcándola como manualmente anulada y registrando el cambio.

        Args:
            note_id: ID de la nota a anular
            user_id: ID del usuario que realiza la anulación
            reason: Razón de la anulación (opcional)

        Returns:
            La nota actualizada
        """
        from ..infrastructure.models import GradeChangeHistory

        note = cls.get_student_note(note_id)

        # Guardar valores anteriores para el historial
        previous_score = note.numeric_score
        previous_qualitative = note.qualitative_scale

        # Marcar como anulada manualmente
        updated = cls.repository.update(
            note_id,
            manually_overridden=True,
            numeric_score=None,
            qualitative_scale_id=None,
        )

        # Registrar en el historial de cambios
        GradeChangeHistory.objects.create(
            student_note=updated,
            modified_by_user_id=user_id,
            previous_score=previous_score or Decimal("0.00"),
            new_score=Decimal("0.00"),
            previous_qualitative=previous_qualitative,
            new_qualitative=None,
            reason=reason or "Nota anulada",
            reason_code="ANULACION",
            origin="MANUAL",
        )

        return updated


class GradeCalculationService:
    """Servicio para calcular resúmenes de calificaciones por periodo y anuales."""

    @staticmethod
    @transaction.atomic
    def calculate_period_summary(enrollment, subject_offering, academic_period):
        from ..infrastructure.models import PromotionStatusChoices

        result = EvaluationRepository.calculate_period_average_for_subject(
            enrollment_id=enrollment.id,
            subject_offering_id=subject_offering.id,
            academic_period_id=academic_period.id,
        )

        if result is None:
            return None

        final_grade = result["final"]
        formative_avg = result["formative"]
        summative_avg = result["summative"]

        is_failing = final_grade < Decimal("7.00")

        summary = PeriodGradeSummaryRepository.get_by_enrollment_offering_period(
            enrollment=enrollment,
            subject_offering=subject_offering,
            academic_period=academic_period,
        )

        promotion_status = PromotionStatusChoices.FAILED if is_failing else PromotionStatusChoices.APPROVED

        if summary:
            PeriodGradeSummaryRepository.update(
                summary.id,
                formative_avg=formative_avg,
                summative_avg=summative_avg,
                final_avg_truncated=final_grade,
                is_failing=is_failing,
                promotion_status=promotion_status,
            )
        else:
            summary = PeriodGradeSummaryRepository.create(
                enrollment=enrollment,
                subject_offering=subject_offering,
                academic_period=academic_period,
                formative_avg=formative_avg,
                summative_avg=summative_avg,
                final_avg_truncated=final_grade,
                is_failing=is_failing,
                promotion_status=promotion_status,
            )

        # Actualizar resumen anual acumulado
        school_year = academic_period.school_year
        GradeCalculationService._update_annual_summary(
            enrollment, subject_offering, school_year
        )

        return summary

    @staticmethod
    @transaction.atomic
    def _update_annual_summary(enrollment, subject_offering, school_year):
        """Calcula o actualiza el resumen anual acumulado para un (enrollment, offering, school_year).

        Promedia todos los períodos disponibles del año usando sus pesos (year_weight).
        Si todos los períodos están cerrados, marca is_finalized=True.
        """
        from ..infrastructure.models import PromotionStatusChoices

        summaries = PeriodGradeSummary.objects.filter(
            enrollment=enrollment,
            subject_offering=subject_offering,
            academic_period__school_year=school_year,
        ).select_related("academic_period")

        if not summaries.exists():
            return None

        total_weight = Decimal("0")
        weighted_sum = Decimal("0")
        all_locked = True

        for s in summaries:
            w = s.academic_period.year_weight or Decimal("0")
            total_weight += w
            weighted_sum += s.final_avg_truncated * w
            if not s.academic_period.grades_locked:
                all_locked = False

        if total_weight == 0:
            return None

        annual_grade = (weighted_sum / total_weight).quantize(Decimal("0.01"))
        is_failing = annual_grade < Decimal("7.00")
        promotion_status = PromotionStatusChoices.FAILED if is_failing else PromotionStatusChoices.APPROVED

        annual = AnnualGradeSummaryRepository.get_by_enrollment_offering_year(
            enrollment, subject_offering, school_year
        )

        if annual:
            AnnualGradeSummaryRepository.update(
                annual.id,
                annual_final_avg=annual_grade,
                is_failing=is_failing,
                promotion_status=promotion_status,
                is_finalized=all_locked,
            )
        else:
            annual = AnnualGradeSummaryRepository.create(
                enrollment=enrollment,
                subject_offering=subject_offering,
                school_year=school_year,
                annual_final_avg=annual_grade,
                is_failing=is_failing,
                promotion_status=promotion_status,
                is_finalized=all_locked,
            )
        return annual

    @staticmethod
    def calculate_all_for_school_year(school_year_id):
        """Calcula los resúmenes anuales para todas las combinaciones
        (enrollment, offering) de un año escolar."""
        from apps.academic.subject_offering.infrastructure.repositories import SubjectOfferingRepository
        from apps.students.repositories.enrollment_repo import EnrollmentRepository
        from apps.institutions.school_year.infrastructure.repositories import SchoolYearRepository

        school_year = SchoolYearRepository.get_by_id(school_year_id)
        if not school_year:
            return []

        offerings = SubjectOfferingRepository.get_by_school_year(school_year_id)
        enrollments = EnrollmentRepository.get_by_school_year(school_year_id)

        results = []
        for offering in offerings:
            for enrollment in enrollments.filter(section_id=offering.section_id):
                annual = GradeCalculationService._update_annual_summary(
                    enrollment, offering, school_year
                )
                if annual:
                    results.append(annual.id)

        return results

    @staticmethod
    def calculate_all_for_period(academic_period_id):
        from apps.academic.academic_period.infrastructure.repositories import AcademicPeriodRepository
        from apps.academic.subject_offering.infrastructure.repositories import SubjectOfferingRepository
        from apps.students.repositories.enrollment_repo import EnrollmentRepository

        period = AcademicPeriodRepository.get_by_id(academic_period_id)
        if not period:
            return []

        offerings = SubjectOfferingRepository.get_by_school_year(period.school_year_id)
        enrollments = EnrollmentRepository.get_by_school_year(period.school_year_id)

        results = []
        for offering in offerings:
            for enrollment in enrollments.filter(section_id=offering.section_id):
                summary = GradeCalculationService.calculate_period_summary(
                    enrollment, offering, period
                )
                if summary:
                    results.append(summary.id)

        return results
