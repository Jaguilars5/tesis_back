from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class StudentEntity:
    id: Optional[int] = None
    user_id: Optional[int] = None
    student_code: str = ""
    has_special_needs: bool = False
    special_needs_type_id: Optional[int] = None
    is_active: bool = True


@dataclass
class EnrollmentEntity:
    id: Optional[int] = None
    student_id: Optional[int] = None
    section_id: Optional[int] = None
    enrollment_status: str = "ACT"
    enrollment_date: Optional[date] = None
    withdrawal_date: Optional[date] = None
    withdrawal_reason_id: Optional[int] = None
    is_repeat: bool = False
