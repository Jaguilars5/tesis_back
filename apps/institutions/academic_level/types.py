from typing import TypedDict


class CreateAcademicLevelPayload(TypedDict, total=False):
    name: str
    code: str
    description: str
