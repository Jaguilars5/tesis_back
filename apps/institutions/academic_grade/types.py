from typing import TypedDict


class CreateAcademicGradePayload(TypedDict, total=False):
    academic_sublevel_id: int
    code: str
    name: str


class UpdateAcademicGradePayload(TypedDict, total=False):
    academic_sublevel_id: int
    code: str
    name: str
    is_active: bool
