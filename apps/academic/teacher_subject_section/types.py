from typing import TypedDict


class CreateTeacherSubjectSectionPayload(TypedDict, total=False):
    user_id: int
    subject_offering_id: int
