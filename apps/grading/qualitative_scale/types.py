from typing import TypedDict


class CreateQualitativeScalePayload(TypedDict, total=False):
    code: str
    name: str
    description: str
    numeric_equivalence: float
