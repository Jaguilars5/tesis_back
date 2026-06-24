from typing import TypedDict


class CreateSubjectOfferingPayload(TypedDict, total=False):
    section_id: int
    subject_academic_config_id: int
