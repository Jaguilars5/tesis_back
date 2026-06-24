from ..domain.entities import ClassScheduleEntity
from .models import ClassSchedule


def to_entity(model: ClassSchedule) -> ClassScheduleEntity:
    return ClassScheduleEntity(
        id=model.id,
        teacher_subject_section_id=model.teacher_subject_section_id,
        day_of_week=model.day_of_week,
        start_time=model.start_time,
        end_time=model.end_time,
        is_active=model.is_active,
    )
