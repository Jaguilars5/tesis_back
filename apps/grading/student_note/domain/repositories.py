from abc import ABC, abstractmethod


class StudentNoteRepositoryInterface(ABC):
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
    def get_by_composite_key(cls, enrollment_id, evaluative_activity_id):
        pass

    @classmethod
    @abstractmethod
    def list_by_filters(cls, student_id=None, academic_period_id=None, subject_id=None, section_id=None):
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
    def update(cls, pk, **data):
        pass

    @classmethod
    @abstractmethod
    def delete(cls, pk):
        pass

    @classmethod
    @abstractmethod
    def get_cascade_counts(cls, instance_id: int) -> dict[str, int]:
        pass

    @classmethod
    @abstractmethod
    def deactivate_cascade(cls, instance_id: int) -> int:
        pass


class PeriodGradeSummaryRepositoryInterface(ABC):
    @classmethod
    @abstractmethod
    def get_by_enrollment_offering_period(cls, enrollment, subject_offering, academic_period):
        pass

    @classmethod
    @abstractmethod
    def count_failing(cls, enrollment_id, academic_period_id):
        pass

    @classmethod
    @abstractmethod
    def create(cls, **data):
        pass

    @classmethod
    @abstractmethod
    def update(cls, pk, **data):
        pass

    @classmethod
    @abstractmethod
    def delete(cls, pk):
        pass

    @classmethod
    @abstractmethod
    def get_cascade_counts(cls, instance_id: int) -> dict[str, int]:
        pass

    @classmethod
    @abstractmethod
    def deactivate_cascade(cls, instance_id: int) -> int:
        pass
