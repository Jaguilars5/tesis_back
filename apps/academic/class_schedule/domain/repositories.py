from abc import ABC, abstractmethod


class ClassScheduleRepositoryInterface(ABC):
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
    def delete(cls, pk):
        pass

    @classmethod
    @abstractmethod
    def get_by_subject_offering(cls, subject_offering_id):
        pass

    @classmethod
    @abstractmethod
    def get_by_teacher(cls, user_id):
        pass

    @classmethod
    @abstractmethod
    def get_by_student(cls, student_id):
        pass

    @classmethod
    @abstractmethod
    def get_by_section(cls, section_id):
        pass

    @classmethod
    @abstractmethod
    def get_today_for_teacher(cls, user_id):
        pass

    @classmethod
    @abstractmethod
    def check_overlap(cls, teacher_subject_section_id, day_of_week, start_time, end_time, exclude_id=None):
        pass
