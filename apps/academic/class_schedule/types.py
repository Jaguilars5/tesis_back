from typing import TypedDict


class CreateClassSchedulePayload(TypedDict, total=False):
    teacher_subject_section_id: int
    day_of_week: int
    start_time: str
    end_time: str
