from typing import TypedDict


class CreatePeriodTypePayload(TypedDict, total=False):
    code: str
    name: str
    description: str
    divisions_per_year: int


class UpdatePeriodTypePayload(TypedDict, total=False):
    code: str
    name: str
    description: str
    divisions_per_year: int
    is_active: bool
