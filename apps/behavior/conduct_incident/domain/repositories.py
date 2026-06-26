from abc import ABC, abstractmethod


class ConductIncidentRepositoryInterface(ABC):
    """Contrato del repositorio de incidentes de conducta."""

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
    def get_by_enrollment_and_period(cls, enrollment_id, academic_period_id):
        pass

    @classmethod
    @abstractmethod
    def get_severe_by_enrollment(cls, enrollment_id, severity_codes=None):
        pass

    @classmethod
    @abstractmethod
    def list_by_filters(cls, student_id=None, academic_period_id=None, category=None, severity=None, family_notified=None):
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

    @classmethod
    @abstractmethod
    def delete(cls, pk):
        pass
