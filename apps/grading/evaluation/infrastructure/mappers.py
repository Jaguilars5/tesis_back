from ..domain.entities import (
    EvaluationBlockEntity,
    BlockComponentEntity,
    EvaluativeActivityEntity,
)
from .models import EvaluationBlock, BlockComponent, EvaluativeActivity


def block_to_entity(model: EvaluationBlock) -> EvaluationBlockEntity:
    return EvaluationBlockEntity(
        id=model.id,
        academic_period_id=model.academic_period_id,
        subject_offering_id=model.subject_offering_id,
        name=model.name,
        block_type=model.block_type,
        weight_percentage=model.weight_percentage,
        is_active=model.is_active,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def component_to_entity(model: BlockComponent) -> BlockComponentEntity:
    return BlockComponentEntity(
        id=model.id,
        evaluation_block_id=model.evaluation_block_id,
        name=model.name,
        internal_weight=model.internal_weight,
        is_active=model.is_active,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def activity_to_entity(model: EvaluativeActivity) -> EvaluativeActivityEntity:
    return EvaluativeActivityEntity(
        id=model.id,
        block_component_id=model.block_component_id,
        teacher_subject_section_id=model.teacher_subject_section_id,
        title=model.title,
        activity_type_id=model.activity_type_id,
        max_score=model.max_score,
        due_date=model.due_date,
        internal_weight=model.internal_weight,
        is_active=model.is_active,
        uuid=str(model.uuid) if model.uuid else None,
        sync_status=model.sync_status,
        sync_version=model.sync_version,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
