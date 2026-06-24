from typing import TypedDict


class CreateActivityTypePayload(TypedDict, total=False):
    code: str
    name: str
    description: str
