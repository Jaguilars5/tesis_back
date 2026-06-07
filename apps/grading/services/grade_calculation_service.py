from decimal import Decimal
from django.db import transaction
from apps.grading.repositories.period_grade_summary_repository import (
    PeriodGradeSummaryRepository,
)
from apps.grading.repositories.evaluation_repo import EvaluationRepository


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

        # Intentar obtener un resumen existente para actualizarlo o crear uno nuevo
        summary = PeriodGradeSummaryRepository.model.objects.filter(
            enrollment=enrollment,
            subject_offering=subject_offering,
            academic_period=academic_period,
        ).first()

        if summary:
            summary.formative_avg = periodo_grade
            summary.final_avg_truncated = periodo_grade
            summary.requires_recovery = requires_recovery
            summary.promotion_status = "recovery" if requires_recovery else "approved"
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
                promotion_status="recovery" if requires_recovery else "approved",
            )
        return summary

    @staticmethod
    def calculate_all_for_period(academic_period_id):
        """
        Calcula resúmenes para todas las matrículas activas en un período.
        Útil para procesos batch vía Celery.
        """
        from apps.academic.models import Academic_Period, SubjectOffering
        from apps.students.models import Enrollment

        try:
            period = Academic_Period.objects.get(pk=academic_period_id)
        except Academic_Period.DoesNotExist:
            return []

        offerings = SubjectOffering.objects.filter(
            school_year_id=period.school_year_id,
            active=True,
        )
        enrollments = Enrollment.objects.filter(
            section__school_year_id=period.school_year_id,
        )

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
