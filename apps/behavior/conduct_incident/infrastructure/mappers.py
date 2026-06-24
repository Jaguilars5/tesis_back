from ..domain.entities import ConductIncidentEntity
from .models import ConductIncident


def to_entity(model: ConductIncident) -> ConductIncidentEntity:
    return ConductIncidentEntity(
        id=model.id,
        incident_type_id=model.incident_type_id,
        severity_id=model.severity_id,
        academic_period_id=model.academic_period_id,
        enrollment_id=model.enrollment_id,
        incident_date=model.incident_date,
        description=model.description,
        actions_taken=model.actions_taken,
        family_notified=model.family_notified,
        uuid=str(model.uuid) if model.uuid else None,
        sync_status=model.sync_status,
        sync_version=model.sync_version,
        device_origin=model.device_origin,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
