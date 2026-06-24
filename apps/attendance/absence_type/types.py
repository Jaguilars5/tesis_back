from typing import TypedDict


class CreateAbsenceTypePayload(TypedDict, total=False):
    code: str
    name: str
    description: str
