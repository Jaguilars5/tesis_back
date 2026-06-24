from decimal import Decimal
from typing import TypedDict


class CreateEvaluationBlockPayload(TypedDict, total=False):
    academic_period_id: int
    subject_offering_id: int
    name: str
    block_type: str
    weight_percentage: Decimal


class CreateBlockComponentPayload(TypedDict, total=False):
    evaluation_block_id: int
    name: str
    internal_weight: Decimal


class CreateEvaluativeActivityPayload(TypedDict, total=False):
    block_component_id: int
    teacher_subject_section_id: int
    title: str
    activity_type_id: int | None
    max_score: Decimal
    due_date: str
    internal_weight: Decimal
