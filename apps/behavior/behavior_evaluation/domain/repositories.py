from abc import ABC, abstractmethod


class BehaviorEvaluationRepositoryInterface(ABC):
    """Contrato del repositorio de evaluaciones de conducta."""

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
    def get_or_create(cls, defaults=None, **lookup):
        pass

    @classmethod
    @abstractmethod
    def update(cls, pk, **data):
        pass
