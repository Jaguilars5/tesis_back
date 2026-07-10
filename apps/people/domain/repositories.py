from abc import ABC, abstractmethod


class CityRepositoryInterface(ABC):
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


class ParishRepositoryInterface(ABC):
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
    def get_by_code(cls, code):
        pass

    @classmethod
    @abstractmethod
    def get_by_city(cls, city_id):
        pass


class DocumentTypeRepositoryInterface(ABC):
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
    def get_by_code(cls, code):
        pass


class PersonRepositoryInterface(ABC):
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
    def get_by_document_number(cls, doc_number):
        pass

    @classmethod
    @abstractmethod
    def search(cls, query):
        pass

    @classmethod
    @abstractmethod
    def get_by_email(cls, email):
        pass
