from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SubjectEntity:
    id: int | None
    name: str
    code: str
    is_active: bool
