from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SubjectOfferingEntity:
    id: int | None
    section_id: int
    subject_academic_config_id: int
    is_active: bool
