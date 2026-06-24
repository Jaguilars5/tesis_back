from typing import TypedDict


class CreateSubjectAcademicConfigPayload(TypedDict, total=False):
    subject_id: int
    academic_grade_id: int
    weekly_hours: int
    is_required: bool
