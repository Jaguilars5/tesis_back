from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal


class AcademicPeriodRepositoryInterface(ABC):
    """Contrato del repositorio de períodos académicos."""

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
    def create(cls, **data):
        pass

    @classmethod
    @abstractmethod
    def update(cls, pk, **data):
        pass

    @classmethod
    @abstractmethod
    def get_by_school_year(cls, school_year_id):
        pass

    @classmethod
    @abstractmethod
    def count_by_school_year_and_period_type(
        cls, school_year_id, period_type_id, exclude_period_id=None
    ):
        pass

    @classmethod
    @abstractmethod
    def sum_year_weight_by_school_year_and_period_type(
        cls, school_year_id, period_type_id, exclude_period_id=None
    ) -> Decimal | int:
        pass

    @classmethod
    @abstractmethod
    def has_overlapping_period(
        cls, school_year_id, start_date, end_date, exclude_period_id=None
    ) -> bool:
        pass

    @classmethod
    @abstractmethod
    def get_period_types_in_school_year(cls, school_year_id, exclude_period_id=None):
        pass
