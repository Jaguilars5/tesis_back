from abc import ABC, abstractmethod
from datetime import date
from typing import Any


class SchoolYearRepositoryInterface(ABC):
    """Contrato del repositorio de años escolares."""

    @classmethod
    @abstractmethod
    def get_all(cls, active_only=True, search=None):
        pass

    @classmethod
    @abstractmethod
    def get_by_id(cls, pk):
        pass

    @classmethod
    @abstractmethod
    def get_current(cls):
        pass

    @classmethod
    @abstractmethod
    def has_overlap(cls, start_date, end_date, exclude_id=None) -> bool:
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
    def get_cascade_counts(cls, instance_id: int) -> dict[str, int]:
        pass

    @classmethod
    @abstractmethod
    def deactivate_cascade(cls, instance_id: int) -> int:
        pass
