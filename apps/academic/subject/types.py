from typing import TypedDict


class CreateSubjectPayload(TypedDict, total=False):
    name: str
    code: str


class UpdateSubjectPayload(TypedDict, total=False):
    name: str
    code: str
    is_active: bool
