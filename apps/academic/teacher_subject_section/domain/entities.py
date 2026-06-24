from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TeacherSubjectSectionEntity:
    id: int | None
    user_id: int
    subject_offering_id: int
    is_active: bool
