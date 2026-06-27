from decimal import Decimal

from django.db import transaction

from ..application import validators
from ..infrastructure.repositories import (
    StudentNoteRepository,
    PeriodGradeSummaryRepository,
    EvaluationRepository,
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
    ):
        errors = validators.run_all_validators(
            enrollment_id=enrollment_id,
            evaluative_activity_id=evaluative_activity_id,
            numeric_score=numeric_score,
        )
        if errors:
            raise ValueError(errors)

        existing = cls.repository.get_by_composite_key(
            enrollment_id, evaluative_activity_id,
        )
        if existing:
            return cls.repository.update(
                existing.id,
                numeric_score=numeric_score,
                teacher_observation=teacher_observation,
                qualitative_scale_id=qualitative_scale_id,
                device_origin=device_origin,
            )

        return cls.repository.create(
            enrollment_id=enrollment_id,
            evaluative_activity_id=evaluative_activity_id,
            numeric_score=numeric_score,
            qualitative_scale_id=qualitative_scale_id,
            teacher_observation=teacher_observation,
        )

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
    def update_student_note(cls, note_id, **kwargs):
        cls.get_student_note(note_id)
        allowed = {
            "numeric_score", "qualitative_scale_id", "teacher_observation",
            "manually_overridden", "grading_mode", "device_origin",
        }
        clean = {k: v for k, v in kwargs.items() if k in allowed}
        return cls.repository.update(note_id, **clean)

    @classmethod
    def calculate_period_average(cls, student_id, academic_period_id, subject_id=None, section_id=None):
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
    """Servicio para calcular res\u00famenes de calificaciones por periodo."""

    @staticmethod
    @transaction.atomic
    def calculate_period_summary(enrollment, subject_offering, academic_period):
        from ..infrastructure.models import PromotionStatusChoices

        periodo_grade = EvaluationRepository.calculate_period_average_for_subject(
            enrollment_id=enrollment.id,
            subject_offering_id=subject_offering.id,
        )

        if periodo_grade is None:
            return None

        is_failing = periodo_grade < Decimal("7.00")

        summary = PeriodGradeSummaryRepository.get_by_enrollment_offering_period(
            enrollment=enrollment,
            subject_offering=subject_offering,
            academic_period=academic_period,
        )

        promotion_status = PromotionStatusChoices.FAILED if is_failing else PromotionStatusChoices.APPROVED

        if summary:
            PeriodGradeSummaryRepository.update(
                summary.id,
                formative_avg=periodo_grade,
                final_avg_truncated=periodo_grade,
                is_failing=is_failing,
                promotion_status=promotion_status,
            )
        else:
            summary = PeriodGradeSummaryRepository.create(
                enrollment=enrollment,
                subject_offering=subject_offering,
                academic_period=academic_period,
                formative_avg=periodo_grade,
                summative_avg=Decimal("0.00"),
                final_avg_truncated=periodo_grade,
                is_failing=is_failing,
                promotion_status=promotion_status,
            )
        return summary

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
