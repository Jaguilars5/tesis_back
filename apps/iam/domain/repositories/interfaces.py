from abc import ABC, abstractmethod


class UserRepositoryInterface(ABC):
    @classmethod
    @abstractmethod
    def get_by_id(cls, user_id):
        pass

    @classmethod
    @abstractmethod
    def get_by_username(cls, username):
        pass

    @classmethod
    @abstractmethod
    def get_all_active(cls):
        pass

    @classmethod
    @abstractmethod
    def get_by_role_code(cls, code):
        pass

    @classmethod
    @abstractmethod
    def search(cls, query_string):
        pass


class RoleRepositoryInterface(ABC):
    @classmethod
    @abstractmethod
    def get_by_id(cls, role_id):
        pass

    @classmethod
    @abstractmethod
    def get_by_name(cls, name):
        pass

    @classmethod
    @abstractmethod
    def get_all(cls):
        pass

    @classmethod
    @abstractmethod
    def get_all_active(cls):
        pass


class PermissionRepositoryInterface(ABC):
    @classmethod
    @abstractmethod
    def get_by_id(cls, permission_id):
        pass

    @classmethod
    @abstractmethod
    def get_by_code(cls, code):
        pass

    @classmethod
    @abstractmethod
    def get_all(cls):
        pass

    @classmethod
    @abstractmethod
    def get_by_module(cls, module):
        pass
