from ..domain.entities import (
    StudentNoteEntity,
    GradeChangeHistoryEntity,
    PeriodGradeSummaryEntity,
)
from .models import StudentNote, GradeChangeHistory, PeriodGradeSummary


def student_note_to_entity(model: StudentNote) -> StudentNoteEntity:
    return StudentNoteEntity(
        id=model.id,
        enrollment_id=model.enrollment_id,
        evaluative_activity_id=model.evaluative_activity_id,
        grading_mode=model.grading_mode,
        qualitative_scale_id=model.qualitative_scale_id,
        numeric_score=model.numeric_score,
        manually_overridden=model.manually_overridden,
        teacher_observation=model.teacher_observation,
        created_by_id=model.created_by_id,
        modified_by_id=model.modified_by_id,
        uuid=str(model.uuid) if model.uuid else None,
        sync_status=model.sync_status,
        sync_version=model.sync_version,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def history_to_entity(model: GradeChangeHistory) -> GradeChangeHistoryEntity:
    return GradeChangeHistoryEntity(
        id=model.id,
        student_note_id=model.student_note_id,
        modified_by_user_id=model.modified_by_user_id,
        previous_score=model.previous_score,
        new_score=model.new_score,
        reason=model.reason,
        origin=model.origin,
        modified_at=model.modified_at,
    )


def summary_to_entity(model: PeriodGradeSummary) -> PeriodGradeSummaryEntity:
    return PeriodGradeSummaryEntity(
        id=model.id,
        enrollment_id=model.enrollment_id,
        subject_offering_id=model.subject_offering_id,
        academic_period_id=model.academic_period_id,
        formative_avg=model.formative_avg,
        summative_avg=model.summative_avg,
        final_avg_truncated=model.final_avg_truncated,
        qualitative_scale_id=model.qualitative_scale_id,
        is_failing=model.is_failing,
        promotion_status=model.promotion_status,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
