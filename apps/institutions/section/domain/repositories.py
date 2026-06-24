from abc import ABC, abstractmethod


class SectionRepositoryInterface(ABC):
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
    def get_by_school_year(cls, school_year_id):
        pass

    @classmethod
    @abstractmethod
    def get_by_grade(cls, academic_grade_id):
        pass

    @classmethod
    @abstractmethod
    def create(cls, **data):
        pass

    @classmethod
    @abstractmethod
    def update(cls, pk, **data):
        pass
