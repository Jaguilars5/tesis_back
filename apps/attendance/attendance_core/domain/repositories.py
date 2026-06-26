from abc import ABC, abstractmethod
from datetime import date


class AttendanceRepositoryInterface(ABC):
    """Contrato del repositorio de asistencias."""

    @classmethod
    @abstractmethod
    def get_all(cls, active_only=True):
        pass

    @classmethod
    @abstractmethod
    def get_by_id(cls, pk):
        pass

    @classmethod
    @abstractmethod
    def get_by_unique_key(cls, enrollment_id, teacher_subject_section_id, attendance_date):
        pass

    @classmethod
    @abstractmethod
    def get_by_unique_key_with_schedule(cls, enrollment_id, class_schedule_id, attendance_date):
        pass

    @classmethod
    @abstractmethod
    def get_students_for_schedule(cls, class_schedule_id, attendance_date):
        pass

    @classmethod
    @abstractmethod
    def get_by_enrollment_and_period(cls, enrollment_id, academic_period_id):
        pass

    @classmethod
    @abstractmethod
    def get_absences_summary(cls, enrollment_id, academic_period_id):
        pass

    @classmethod
    @abstractmethod
    def list_by_filters(cls, student_id=None, academic_period_id=None, section_id=None, date=None, status=None):
        pass

    @classmethod
    @abstractmethod
    def list_for_risk_snapshot(cls, student_id, academic_period_id):
        pass

    @classmethod
    @abstractmethod
    def create(cls, **data):
        pass

    @classmethod
    @abstractmethod
    def get_cascade_counts(cls, instance_id: int) -> dict[str, int]:
        pass

    @classmethod
    @abstractmethod
    def deactivate_cascade(cls, instance_id: int) -> int:
        pass

    @classmethod
    @abstractmethod
    def update(cls, pk, **data):
        pass
