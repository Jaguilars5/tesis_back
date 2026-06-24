from decimal import Decimal

from django.db import transaction

from ..infrastructure.repositories import (
    StudentNoteRepository,
    PeriodGradeSummaryRepository,
)


class StudentNoteService:
    """L\u00f3gica de negocio para notas de estudiantes."""

    @staticmethod
    @transaction.atomic
    def create_student_note(
        enrollment_id,
        evaluative_activity_id,
        numeric_score,
        qualitative_scale_id=None,
        teacher_observation="",
        device_origin=None,
    ):
        existing = StudentNoteRepository.get_by_composite_key(
            enrollment_id, evaluative_activity_id,
        )
        if existing:
            existing.numeric_score = numeric_score
            existing.teacher_observation = teacher_observation
            existing.sync_status = "PENDING"
            existing.device_origin = device_origin
            if qualitative_scale_id:
                existing.qualitative_scale_id = qualitative_scale_id
            existing.full_clean()
            existing.save()
            return existing

        from ..infrastructure.models import StudentNote

        note = StudentNote(
            enrollment_id=enrollment_id,
            evaluative_activity_id=evaluative_activity_id,
            numeric_score=numeric_score,
            qualitative_scale_id=qualitative_scale_id,
            teacher_observation=teacher_observation,
        )
        note.full_clean()
        note.save()
        return note

    @staticmethod
    def get_student_note(note_id):
        note = StudentNoteRepository.get_by_id(note_id)
        if not note:
            raise ValueError(f"Calificaci\u00f3n {note_id} no encontrada")
        return note

    @staticmethod
    def list_student_notes(student_id=None, academic_period_id=None, subject_id=None, section_id=None):
        return StudentNoteRepository.list_by_filters(
            student_id=student_id,
            academic_period_id=academic_period_id,
            subject_id=subject_id,
            section_id=section_id,
        )

    @staticmethod
    @transaction.atomic
    def update_student_note(note_id, **kwargs):
        note = StudentNoteService.get_student_note(note_id)
        for key, value in kwargs.items():
            if hasattr(note, key):
                setattr(note, key, value)
        note.full_clean()
        note.save()
        return note

    @staticmethod
    def deactivate_student_note(note_id):
        note = StudentNoteService.get_student_note(note_id)
        note.manually_overridden = True
        note.save()
        return note

    @staticmethod
    def calculate_period_average(student_id, academic_period_id, subject_id=None, section_id=None):
        queryset = StudentNoteRepository.list_by_filters(
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


class GradeCalculationService:
    """Servicio para calcular res\u00famenes de calificaciones por per\u00edodo."""

    @staticmethod
    @transaction.atomic
    def calculate_period_summary(enrollment, subject_offering, academic_period):
        from ..infrastructure.models import PeriodGradeSummary

        from ..infrastructure.repositories import EvaluationRepository

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

        from ..infrastructure.models import PromotionStatusChoices

        promotion_status = PromotionStatusChoices.FAILED if is_failing else PromotionStatusChoices.APPROVED

        if summary:
            summary.formative_avg = periodo_grade
            summary.final_avg_truncated = periodo_grade
            summary.is_failing = is_failing
            summary.promotion_status = promotion_status
            summary.save()
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
