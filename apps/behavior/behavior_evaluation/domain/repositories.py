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
    def create(cls, **data):
        pass

    @classmethod
    @abstractmethod
    def get_or_create(cls, defaults=None, **lookup):
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
    def get_qualitative_scale_by_code(cls, code):
        pass

    @classmethod
    @abstractmethod
    def get_or_create_qualitative_scale(cls, code, defaults=None):
        pass
