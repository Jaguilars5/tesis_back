import logging

from celery import shared_task

from apps.integration.tasks.sync_tasks import BaseSyncHandler, register_sync_handler

from .infrastructure.models import StudentNote
from .domain.services import GradeCalculationService

logger = logging.getLogger(__name__)


@register_sync_handler("student_note")
class StudentNoteSyncHandler(BaseSyncHandler):
    source_table = "student_note"
    model = StudentNote
    business_key_fields = ["enrollment_id", "evaluative_activity_id"]


@shared_task(bind=True, ignore_result=True)
def recompute_period_grade_summary_task(self, enrollment_id, subject_offering_id, academic_period_id):
    from apps.students.repositories.enrollment_repo import EnrollmentRepository
    from apps.academic.academic_period.infrastructure.repositories import (
        AcademicPeriodRepository,
    )
    from apps.academic.subject_offering.infrastructure.repositories import (
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


@shared_task(bind=True, ignore_result=True)
def calculate_annual_grade_summaries_task(self, school_year_id):
    from apps.institutions.school_year.infrastructure.repositories import (
        SchoolYearRepository,
    )

    logger.info(
        "calculate_annual_grade_summaries_task start school_year_id=%s task_id=%s",
        school_year_id, getattr(self.request, "id", None),
    )

    school_year = SchoolYearRepository.get_by_id(school_year_id)
    if not school_year:
        logger.warning(
            "calculate_annual_grade_summaries_task skipped: school_year %s not found",
            school_year_id,
        )
        return None

    ids = GradeCalculationService.calculate_all_for_school_year(school_year_id)
    logger.info(
        "calculate_annual_grade_summaries_task done: %s summaries calculated",
        len(ids),
    )
    return ids
