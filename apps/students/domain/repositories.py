from abc import ABC, abstractmethod


class StudentRepositoryInterface(ABC):
    @classmethod
    @abstractmethod
    def get_all(cls, active_only=True): ...

    @classmethod
    @abstractmethod
    def get_by_id(cls, pk): ...

    @classmethod
    @abstractmethod
    def get_by_dni(cls, dni): ...

    @classmethod
    @abstractmethod
    def get_by_section(cls, section_id): ...

    @classmethod
    @abstractmethod
    def search(cls, query): ...

    @classmethod
    @abstractmethod
    def create(cls, **data): ...

    @classmethod
    @abstractmethod
    def update(cls, pk, **data): ...

    @classmethod
    @abstractmethod
    def delete(cls, pk): ...


class StudentRepresentativeRepositoryInterface(ABC):
    @classmethod
    @abstractmethod
    def get_all(cls, active_only=True): ...

    @classmethod
    @abstractmethod
    def get_by_id(cls, pk): ...

    @classmethod
    @abstractmethod
    def get_by_student(cls, student_id): ...

    @classmethod
    @abstractmethod
    def get_by_person(cls, user_id): ...

    @classmethod
    @abstractmethod
    def get_relationship(cls, student_id, user_id): ...

    @classmethod
    @abstractmethod
    def create(cls, **data): ...


class EnrollmentRepositoryInterface(ABC):
    @classmethod
    @abstractmethod
    def get_all(cls, active_only=True): ...

    @classmethod
    @abstractmethod
    def get_by_id(cls, pk): ...

    @classmethod
    @abstractmethod
    def get_active_by_student(cls, student_id): ...

    @classmethod
    @abstractmethod
    def get_by_section(cls, section_id): ...

    @classmethod
    @abstractmethod
    def get_by_school_year(cls, school_year_id): ...

    @classmethod
    @abstractmethod
    def get_students_by_section(cls, section_id, status_code="ACT"): ...

    @classmethod
    @abstractmethod
    def count_active_in_section(cls, section_id): ...

    @classmethod
    @abstractmethod
    def has_active_enrollment(cls, student_id): ...

    @classmethod
    @abstractmethod
    def get_by_representative(cls, user): ...

    @classmethod
    @abstractmethod
    def create(cls, **data): ...
