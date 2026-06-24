from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AcademicGradeEntity:
    id: int | None
    academic_sublevel_id: int | None
    code: str
    name: str
    is_active: bool
