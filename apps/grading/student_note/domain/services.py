from decimal import Decimal

from django.db import transaction

from ..application import validators
from ..infrastructure.repositories import (
    StudentNoteRepository,
    PeriodGradeSummaryRepository,
    EvaluationRepository,
)


class StudentNoteService:
    """L\u00f3gica de negocio para notas de estudiantes."""

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
            raise ValueError(f"Calificaci\u00f3n {note_id} no encontrada")
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
    def soft_delete(cls, pk, confirm=False):
        obj = cls.get_student_note(pk)
        counts = cls.repository.get_cascade_counts(pk)
        total = sum(counts.values())

        if total > 0 and not confirm:
            parts = [f"{v} {k}" for k, v in counts.items()]
            return {
                "requires_confirmation": True,
                "affected_records": total,
                "message": f"Esta acci\u00f3n desactivar\u00e1 {', '.join(parts)} relacionados",
                "id": obj.id,
                "is_active": True,
            }

        total = cls.repository.deactivate_cascade(pk)
        return {
            "id": obj.id,
            "is_active": False,
            "deactivated_records": total,
        }


class GradeCalculationService:
    """Servicio para calcular res\u00famenes de calificaciones por per\u00edodo."""

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
