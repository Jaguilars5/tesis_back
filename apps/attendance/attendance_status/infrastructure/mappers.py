from ..domain.entities import AttendanceStatusEntity
from .models import AttendanceStatus


def to_entity(model: AttendanceStatus) -> AttendanceStatusEntity:
    return AttendanceStatusEntity(
        id=model.id,
        code=model.code,
        name=model.name,
        description=model.description,
        is_active=model.is_active,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
