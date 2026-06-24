from typing import TypedDict


class CreateAttendanceStatusPayload(TypedDict, total=False):
    code: str
    name: str
    description: str
