from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SubjectAcademicConfigEntity:
    id: int | None
    subject_id: int
    academic_grade_id: int
    weekly_hours: int
    is_required: bool
    is_active: bool
