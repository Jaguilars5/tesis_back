from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class StudentNoteEntity:
    id: int | None
    enrollment_id: int
    evaluative_activity_id: int
    grading_mode: str
    qualitative_scale_id: int | None
    numeric_score: Decimal | None
    manually_overridden: bool
    teacher_observation: str
    created_by_id: int | None
    modified_by_id: int | None
    uuid: str | None
    sync_status: str
    sync_version: int
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class GradeChangeHistoryEntity:
    id: int | None
    student_note_id: int
    modified_by_user_id: int | None
    previous_score: Decimal
    new_score: Decimal
    reason: str
    origin: str
    modified_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class PeriodGradeSummaryEntity:
    id: int | None
    enrollment_id: int
    subject_offering_id: int
    academic_period_id: int
    formative_avg: Decimal
    summative_avg: Decimal
    final_avg_truncated: Decimal
    qualitative_scale_id: int | None
    is_failing: bool
    promotion_status: str | None
    created_at: datetime | None = None
    updated_at: datetime | None = None
