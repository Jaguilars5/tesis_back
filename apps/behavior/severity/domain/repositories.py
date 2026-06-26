from abc import ABC, abstractmethod


class SeverityRepositoryInterface(ABC):
    """Contrato del repositorio de severidades."""

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
    def get_cascade_counts(cls, instance_id: int) -> dict[str, int]:
        pass

    @classmethod
    @abstractmethod
    def deactivate_cascade(cls, instance_id: int) -> int:
        pass

    @classmethod
    @abstractmethod
    def delete(cls, pk):
        pass
