import logging

from celery import shared_task

from apps.integration.tasks.sync_tasks import BaseSyncHandler, register_sync_handler
from apps.grading.models import (
    StudentNote, EvaluativeActivity,
)
from apps.grading.services.grade_calculation_service import GradeCalculationService


logger = logging.getLogger(__name__)


@register_sync_handler("student_note")
class StudentNoteSyncHandler(BaseSyncHandler):
    source_table = "student_note"
    model = StudentNote


@register_sync_handler("evaluative_activity")
class EvaluativeActivitySyncHandler(BaseSyncHandler):
    source_table = "evaluative_activity"
    model = EvaluativeActivity


@shared_task(bind=True, ignore_result=True)
def recompute_period_grade_summary_task(self, enrollment_id, subject_offering_id, academic_period_id):
    """
    Recalcula el PeriodGradeSummary para (enrollment, subject_offering, academic_period).
    Disparado por signals en StudentNote o por la acción 'recalculate' del ViewSet.
    Los reintentos los maneja el caller (signal con on_commit) — en eager
    (tests) no se reintenta para mantener la suite rápida.
    """
    from apps.students.repositories.enrollment_repo import EnrollmentRepository
    from apps.academic.repositories.academic_repo import (
        AcademicPeriodRepository,
        SubjectOfferingRepository,
    )

    logger.info(
        "recompute_period_grade_summary_task start enrollment_id=%s "
        "subject_offering_id=%s academic_period_id=%s task_id=%s",
        enrollment_id, subject_offering_id, academic_period_id,
        getattr(self.request, "id", None),
    )

    enrollment = EnrollmentRepository.get_by_id(enrollment_id)
    offering = SubjectOfferingRepository.get_by_id(subject_offering_id)
    period = AcademicPeriodRepository.get_by_id(academic_period_id)

    if not (enrollment and offering and period):
        logger.warning(
            "recompute_period_grade_summary_task skipped: missing entity "
            "(enrollment=%s, offering=%s, period=%s)",
            bool(enrollment), bool(offering), bool(period),
        )
        return None

    return GradeCalculationService.calculate_period_summary(
        enrollment=enrollment,
        subject_offering=offering,
        academic_period=period,
    )
