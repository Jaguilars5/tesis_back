from decimal import Decimal
from django.db import transaction
from apps.academic.repositories.academic_repo import (
    AcademicPeriodRepository,
    SubjectOfferingRepository,
)
from apps.students.repositories.enrollment_repo import EnrollmentRepository
from ..models import PromotionStatus
from ..repositories.period_grade_summary_repository import (
    PeriodGradeSummaryRepository,
)
from ..repositories.evaluation_repo import EvaluationRepository


class GradeCalculationService:
    """
    Servicio para calcular resúmenes de calificaciones por período.
    Depende de EvaluationRepository para obtener notas y ponderaciones.
    """

    @staticmethod
    @transaction.atomic
    def calculate_period_summary(enrollment, subject_offering, academic_period):
        """
        Calcula el resumen de calificaciones para una matrícula,
        oferta de asignatura y período específicos.
        """
        periodo_grade = EvaluationRepository.calculate_period_average_for_subject(
            enrollment_id=enrollment.id,
            subject_offering_id=subject_offering.id,
        )

        if periodo_grade is None:
            return None

        requires_recovery = periodo_grade < Decimal("7.00")

        summary = PeriodGradeSummaryRepository.get_by_enrollment_offering_period(
            enrollment=enrollment,
            subject_offering=subject_offering,
            academic_period=academic_period,
        )

        promo_code = "RECUPERACION" if requires_recovery else "APROBADO"
        promo_name = "Recuperación" if requires_recovery else "Aprobado"
        promotion_status, _ = PromotionStatus.objects.get_or_create(
            code=promo_code,
            defaults={"name": promo_name},
        )

        if summary:
            summary.formative_avg = periodo_grade
            summary.final_avg_truncated = periodo_grade
            summary.requires_recovery = requires_recovery
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
                requires_recovery=requires_recovery,
                promotion_status=promotion_status,
            )
        return summary

    @staticmethod
    def calculate_all_for_period(academic_period_id):
        """
        Calcula resúmenes para todas las matrículas activas en un período.
        Útil para procesos batch vía Celery.
        """
        period = AcademicPeriodRepository.get_by_id(academic_period_id)
        if not period:
            return []

        offerings = SubjectOfferingRepository.get_by_school_year(
            period.school_year_id
        )
        enrollments = EnrollmentRepository.get_by_school_year(period.school_year_id)

        results = []
        for offering in offerings:
            for enrollment in enrollments.filter(
                section_id=offering.section_id
            ):
                summary = GradeCalculationService.calculate_period_summary(
                    enrollment, offering, period
                )
                if summary:
                    results.append(summary.id)

        return results
