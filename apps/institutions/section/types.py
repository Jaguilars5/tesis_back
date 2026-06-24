from typing import TypedDict


class CreateSectionPayload(TypedDict, total=False):
    school_year_id: int
    academic_grade_id: int
    parallel: str
    capacity: int
    code: str
