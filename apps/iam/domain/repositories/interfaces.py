from abc import ABC, abstractmethod


class UserRepositoryInterface(ABC):
    @classmethod
    @abstractmethod
    def get_by_id(cls, user_id): ...

    @classmethod
    @abstractmethod
    def get_by_username(cls, username): ...

    @classmethod
    @abstractmethod
    def get_by_email(cls, email): ...

    @classmethod
    @abstractmethod
    def get_by_dni(cls, dni): ...

    @classmethod
    @abstractmethod
    def get_all_active(cls): ...

    @classmethod
    @abstractmethod
    def get_by_role(cls, role_id): ...

    @classmethod
    @abstractmethod
    def get_by_role_code(cls, code): ...

    @classmethod
    @abstractmethod
    def create_user(cls, person, password, is_superuser=False, **extra_fields): ...

    @classmethod
    @abstractmethod
    def update_user(cls, user, **kwargs): ...

    @classmethod
    @abstractmethod
    def delete_user(cls, user): ...

    @classmethod
    @abstractmethod
    def change_password(cls, user, new_password): ...

    @classmethod
    @abstractmethod
    def bulk_create(cls, user_list): ...

    @classmethod
    @abstractmethod
    def search(cls, query_string): ...

    @classmethod
    @abstractmethod
    def search_by_role_code(cls, role_code, search=None): ...

    @classmethod
    @abstractmethod
    def create_user_with_person(cls, document_number, names, last_names, email, password, role_id): ...

    @classmethod
    @abstractmethod
    def add_user_role(cls, user, role): ...


class RoleRepositoryInterface(ABC):
    @classmethod
    @abstractmethod
    def get_by_id(cls, role_id): ...

    @classmethod
    @abstractmethod
    def get_by_name(cls, name): ...

    @classmethod
    @abstractmethod
    def get_all(cls): ...

    @classmethod
    @abstractmethod
    def get_all_active(cls): ...

    @classmethod
    @abstractmethod
    def create_role(cls, name, description="", active=True): ...

    @classmethod
    @abstractmethod
    def update_role(cls, role, **kwargs): ...

    @classmethod
    @abstractmethod
    def delete_role(cls, role): ...

    @classmethod
    @abstractmethod
    def get_permissions(cls, role_id): ...

    @classmethod
    @abstractmethod
    def add_permission(cls, role, permission): ...

    @classmethod
    @abstractmethod
    def remove_permission(cls, role, permission): ...

    @classmethod
    @abstractmethod
    def set_permissions(cls, role, permission_objects): ...

    @classmethod
    @abstractmethod
    def get_cascade_counts(cls, instance_id: int) -> dict[str, int]: ...

    @classmethod
    @abstractmethod
    def deactivate_cascade(cls, instance_id: int) -> int: ...


class PermissionRepositoryInterface(ABC):
    @classmethod
    @abstractmethod
    def get_by_id(cls, permission_id): ...

    @classmethod
    @abstractmethod
    def get_by_code(cls, code): ...

    @classmethod
    @abstractmethod
    def get_all(cls): ...

    @classmethod
    @abstractmethod
    def get_by_module(cls, module): ...

    @classmethod
    @abstractmethod
    def create_permission(cls, code, description="", module=""): ...

    @classmethod
    @abstractmethod
    def create_many(cls, permission_list): ...

    @classmethod
    @abstractmethod
    def update_permission(cls, permission, **kwargs): ...

    @classmethod
    @abstractmethod
    def delete_permission(cls, permission): ...

    @classmethod
    @abstractmethod
    def count_role_permissions(cls, permission_id): ...

    @classmethod
    @abstractmethod
    def search(cls, query_string): ...
