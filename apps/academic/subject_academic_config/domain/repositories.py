from abc import ABC, abstractmethod


class SubjectAcademicConfigRepositoryInterface(ABC):
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
    def get_by_subject(cls, subject_id):
        pass

    @classmethod
    @abstractmethod
    def get_by_grade(cls, academic_grade_id):
        pass

    @classmethod
    @abstractmethod
    def exists(cls, **filters):
        pass
