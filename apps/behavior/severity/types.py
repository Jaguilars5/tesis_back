from typing import TypedDict


class CreateSeverityPayload(TypedDict, total=False):
    code: str
    name: str
    description: str
