from abc import ABC, abstractmethod


class SubjectOfferingRepositoryInterface(ABC):
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
    def get_by_section(cls, section_id, school_year_id=None):
        pass

    @classmethod
    @abstractmethod
    def get_by_school_year(cls, school_year_id):
        pass

    @classmethod
    @abstractmethod
    def exists(cls, **filters):
        pass
