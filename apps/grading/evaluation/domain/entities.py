from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class EvaluationBlockEntity:
    id: int | None
    academic_period_id: int
    subject_offering_id: int
    name: str
    block_type: str | None
    weight_percentage: Decimal
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class BlockComponentEntity:
    id: int | None
    evaluation_block_id: int
    name: str
    internal_weight: Decimal
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class EvaluativeActivityEntity:
    id: int | None
    block_component_id: int
    teacher_subject_section_id: int
    title: str
    activity_type_id: int | None
    max_score: Decimal
    due_date: date
    internal_weight: Decimal
    is_active: bool
    uuid: str | None
    sync_status: str
    sync_version: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
