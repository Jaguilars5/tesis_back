"""
Interfaces de repositorio (Abstract Base Classes) para riesgo estudiantil.
"""

from abc import ABC, abstractmethod
from typing import List, Optional


class RiskFactorRepositoryInterface(ABC):
    """Interface para repositorio de factores de riesgo."""

    @classmethod
    @abstractmethod
    def get_all(cls, active_only: bool = True) -> List:
        pass

    @classmethod
    @abstractmethod
    def get_by_id(cls, pk: int):
        pass

    @classmethod
    @abstractmethod
    def get_by_code(cls, code: str):
        pass


class StudentRiskScoreRepositoryInterface(ABC):
    """Interface para repositorio de puntajes de riesgo."""

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
    def get_by_enrollment(cls, enrollment_id: int):
        pass

    @classmethod
    @abstractmethod
    def get_by_period(cls, academic_period_id: int):
        pass


class StudentRiskFactorRepositoryInterface(ABC):
    """Interface para repositorio de factores por estudiante."""

    @classmethod
    @abstractmethod
    def get_by_score(cls, score_id: int):
        pass


class StudentFeatureSnapshotRepositoryInterface(ABC):
    """Interface para repositorio de snapshots."""

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
    def get_by_period(cls, academic_period_id: int):
        pass
