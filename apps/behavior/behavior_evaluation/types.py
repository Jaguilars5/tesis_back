from datetime import date
from typing import TypedDict


class CalculateEvaluationPayload(TypedDict, total=False):
    enrollment_id: int
    academic_period_id: int


class OverrideEvaluationPayload(TypedDict, total=False):
    final_scale_id: int
    reason: str
