from ..domain.entities import BehaviorEvaluationEntity
from .models import BehaviorEvaluation


def to_entity(model: BehaviorEvaluation) -> BehaviorEvaluationEntity:
    return BehaviorEvaluationEntity(
        id=model.id,
        enrollment_id=model.enrollment_id,
        academic_period_id=model.academic_period_id,
        evaluated_by_id=model.evaluated_by_id,
        approved_by_id=model.approved_by_id,
        created_by_id=model.created_by_id,
        calculated_scale_id=model.calculated_scale_id,
        final_scale_id=model.final_scale_id,
        general_observation=model.general_observation,
        override_reason=model.override_reason,
        evaluation_date=model.evaluation_date,
        approval_date=model.approval_date,
        uuid=str(model.uuid) if model.uuid else None,
        sync_status=model.sync_status,
        sync_version=model.sync_version,
        device_origin=model.device_origin,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
