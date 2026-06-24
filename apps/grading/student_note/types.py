from decimal import Decimal
from typing import TypedDict


class CreateStudentNotePayload(TypedDict, total=False):
    enrollment_id: int
    evaluative_activity_id: int
    grading_mode: str
    qualitative_scale_id: int | None
    numeric_score: Decimal | None
    teacher_observation: str
    created_by_id: int | None


class RecalculatePayload(TypedDict, total=False):
    enrollment_id: int
    subject_offering_id: int
    academic_period_id: int
