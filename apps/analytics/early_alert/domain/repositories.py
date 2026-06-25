from abc import ABC, abstractmethod
from typing import List, Optional


class EarlyAlertRepositoryInterface(ABC):
    @classmethod
    @abstractmethod
    def get_all(cls, active_only: bool = True):
        pass

    @classmethod
    @abstractmethod
    def get_by_id(cls, pk: int):
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
    def get_pending_alerts(cls, urgency_level: Optional[str] = None):
        pass

    @classmethod
    @abstractmethod
    def get_by_enrollment(cls, enrollment_id: int):
        pass

    @classmethod
    @abstractmethod
    def count_active_by_enrollment(cls, enrollment_id: int) -> int:
        pass

    @classmethod
    @abstractmethod
    def get_pending_count(cls) -> int:
        pass

    @classmethod
    @abstractmethod
    def get_by_urgency(cls, urgency_level: str):
        pass

    @classmethod
    @abstractmethod
    def get_cascade_counts(cls, instance_id: int) -> dict[str, int]:
        pass

    @classmethod
    @abstractmethod
    def deactivate_cascade(cls, instance_id: int) -> int:
        pass
