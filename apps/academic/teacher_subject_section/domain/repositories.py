from abc import ABC, abstractmethod


class TeacherSubjectSectionRepositoryInterface(ABC):
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
    def get_by_user(cls, user_id, school_year_id=None):
        pass

    @classmethod
    @abstractmethod
    def get_by_section(cls, section_id):
        pass

    @classmethod
    @abstractmethod
    def get_by_subject_offering(cls, subject_offering_id):
        pass

    @classmethod
    @abstractmethod
    def get_by_subject(cls, subject_id):
        pass

    @classmethod
    @abstractmethod
    def exists_by_user_and_offering(cls, user_id, subject_offering_id):
        pass

    @classmethod
    @abstractmethod
    def filter_by_assignments(cls, user_id=None, subject_offering_id=None):
        pass

    @classmethod
    @abstractmethod
    def get_cascade_counts(cls, instance_id: int) -> dict[str, int]:
        pass

    @classmethod
    @abstractmethod
    def deactivate_cascade(cls, instance_id: int) -> int:
        pass
