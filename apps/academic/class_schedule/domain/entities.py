from dataclasses import dataclass
from datetime import time


@dataclass(frozen=True, slots=True)
class ClassScheduleEntity:
    id: int | None
    teacher_subject_section_id: int
    day_of_week: int
    start_time: time
    end_time: time
    is_active: bool
