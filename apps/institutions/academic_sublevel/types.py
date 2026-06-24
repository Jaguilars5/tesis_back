from typing import TypedDict


class CreateAcademicSublevelPayload(TypedDict, total=False):
    academic_level_id: int
    code: str
    name: str
    description: str
