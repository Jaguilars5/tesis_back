from datetime import date
from typing import TypedDict


class CreateConductIncidentPayload(TypedDict, total=False):
    incident_type_id: int
    severity_id: int
    academic_period_id: int
    enrollment_id: int
    incident_date: date
    description: str
    actions_taken: str
    family_notified: bool
