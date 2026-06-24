from typing import TypedDict


class CreateIncidentTypePayload(TypedDict, total=False):
    code: str
    name: str
    description: str
