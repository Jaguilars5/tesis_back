"""Capa de dominio del m\u00f3dulo IAM — Servicios."""

from django.contrib.auth.password_validation import validate_password

from ..infrastructure.repositories import (
    UserRepository,
    RoleRepository,
    PermissionRepository,
)
from ..infrastructure.models import User, UserRole


class UserService:
    def __init__(self):
        self.user_repo = UserRepository()
        self.role_repo = RoleRepository()
        self.permission_repo = PermissionRepository()

    def create_user(self, document_number, names, last_names, email, password, role_id):
        existing_email = self.user_repo.get_by_email(email)
        if existing_email:
            raise ValueError(f"El email {email} ya est\u00e1 registrado")

        existing_dni = self.user_repo.get_by_dni(document_number)
        if existing_dni:
            raise ValueError(f"El DNI {document_number} ya est\u00e1 registrado")

        role = self.role_repo.get_by_id(role_id)
        if not role:
            raise ValueError(f"El rol con ID {role_id} no existe")

        from apps.people.models import DocumentType, Person

        doc_type = DocumentType.objects.get_or_create(
            code="CC", defaults={"name": "C\u00e9dula de Ciudadan\u00eda"}
        )[0]
        person = Person.objects.create(
            document_type=doc_type,
            document_number=document_number,
            names=names,
            last_names=last_names,
            email=email,
        )

        user = self.user_repo.create_user(person=person, password=password)
        UserRole.objects.create(user=user, role=role)
        return user

    def get_user(self, user_id):
        return self.user_repo.get_by_id(user_id)

    def get_user_by_email(self, email):
        return self.user_repo.get_by_email(email)

    def get_user_by_username(self, username):
        return self.user_repo.get_by_username(username)

    def list_users(self):
        return self.user_repo.get_all_active()

    def list_users_by_role(self, role_id):
        return self.user_repo.get_by_role(role_id)

    def list_users_by_role_code(self, code):
        return self.user_repo.get_by_role_code(code)

    def update_user(self, user_id, **kwargs):
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"Usuario con ID {user_id} no existe")
        current_email = user.person.email if user.person else None
        if "email" in kwargs and kwargs["email"] != current_email:
            existing = self.user_repo.get_by_email(kwargs["email"])
            if existing and existing.id != user.id:
                raise ValueError(f"El email {kwargs['email']} ya est\u00e1 registrado")
        if "role" in kwargs:
            role = self.role_repo.get_by_id(kwargs["role"])
            if not role:
                raise ValueError(f"El rol con ID {kwargs['role']} no existe")
        return self.user_repo.update_user(user, **kwargs)

    def change_password(self, user_id, new_password):
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"Usuario con ID {user_id} no existe")
        validate_password(new_password, user=user)
        user.set_password(new_password)
        user.must_change_password = False
        user.save(update_fields=["password", "must_change_password", "updated_at"])
        return user

    def deactivate_user(self, user_id):
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"Usuario con ID {user_id} no existe")
        self.user_repo.delete_user(user)
        return user

    def has_permission(self, user_id, permission_code):
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return False
        return user.has_perm(permission_code)

    def get_user_permissions(self, user_id):
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return set()
        return user.get_all_permissions()

    def search_users(self, query_string):
        return self.user_repo.search(query_string)


class RoleService:
    def __init__(self):
        self.role_repo = RoleRepository()
        self.permission_repo = PermissionRepository()

    def create_role(self, name, description="", active=True):
        existing = self.role_repo.get_by_name(name)
        if existing:
            raise ValueError(f"El rol '{name}' ya existe")
        return self.role_repo.create_role(name, description, active)

    def get_role(self, role_id):
        return self.role_repo.get_by_id(role_id)

    def get_role_by_name(self, name):
        return self.role_repo.get_by_name(name)

    def list_roles(self, only_active=True):
        if only_active:
            return self.role_repo.get_all_active()
        return self.role_repo.get_all()

    def update_role(self, role_id, **kwargs):
        role = self.role_repo.get_by_id(role_id)
        if not role:
            raise ValueError(f"Rol con ID {role_id} no existe")
        if "name" in kwargs and kwargs["name"] != role.name:
            existing = self.role_repo.get_by_name(kwargs["name"])
            if existing:
                raise ValueError(f"El rol '{kwargs['name']}' ya existe")
        return self.role_repo.update_role(role, **kwargs)

    def deactivate_role(self, role_id):
        role = self.role_repo.get_by_id(role_id)
        if not role:
            raise ValueError(f"Rol con ID {role_id} no existe")
        active_users = len(UserRepository.get_by_role(role_id))
        if active_users > 0:
            raise ValueError(
                f"No se puede desactivar el rol '{role.name}' porque hay {active_users} usuarios activos asignados"
            )
        self.role_repo.delete_role(role)
        return role

    def get_role_permissions(self, role_id):
        return self.role_repo.get_permissions(role_id)

    def add_permission_to_role(self, role_id, permission_code):
        role = self.role_repo.get_by_id(role_id)
        if not role:
            raise ValueError(f"Rol con ID {role_id} no existe")
        permission = self.permission_repo.get_by_code(permission_code)
        if not permission:
            raise ValueError(f"El permiso {permission_code} no existe")
        rp, created = self.role_repo.add_permission(role, permission)
        return rp, created

    def remove_permission_from_role(self, role_id, permission_code):
        role = self.role_repo.get_by_id(role_id)
        if not role:
            raise ValueError(f"Rol con ID {role_id} no existe")
        permission = self.permission_repo.get_by_code(permission_code)
        if not permission:
            raise ValueError(f"El permiso {permission_code} no existe")
        deleted_count, _ = self.role_repo.remove_permission(role, permission)
        return deleted_count > 0

    def assign_permissions_to_role(self, role_id, permission_codes):
        role = self.role_repo.get_by_id(role_id)
        if not role:
            raise ValueError(f"Rol con ID {role_id} no existe")
        permissions = self.permission_repo.get_all()
        permission_dict = {p.code: p for p in permissions}
        for code in permission_codes:
            if code not in permission_dict:
                raise ValueError(f"El permiso {code} no existe")
        permission_objs = [permission_dict[c] for c in permission_codes]
        self.role_repo.set_permissions(role, permission_objs)
        return len(permission_objs)


class PermissionService:
    def __init__(self):
        self.permission_repo = PermissionRepository()

    def create_permission(self, code, description="", module=""):
        existing = self.permission_repo.get_by_code(code)
        if existing:
            raise ValueError(f"El permiso '{code}' ya existe")
        return self.permission_repo.create_permission(code, description, module)

    def create_permissions_bulk(self, permission_list):
        return self.permission_repo.create_many(permission_list)

    def get_permission(self, permission_id):
        return self.permission_repo.get_by_id(permission_id)

    def get_permission_by_code(self, code):
        return self.permission_repo.get_by_code(code)

    def list_permissions(self):
        return self.permission_repo.get_all()

    def list_permissions_by_module(self, module):
        return self.permission_repo.get_by_module(module)

    def update_permission(self, permission_id, **kwargs):
        permission = self.permission_repo.get_by_id(permission_id)
        if not permission:
            raise ValueError(f"Permiso con ID {permission_id} no existe")
        return self.permission_repo.update_permission(permission, **kwargs)

    def delete_permission(self, permission_id):
        permission = self.permission_repo.get_by_id(permission_id)
        if not permission:
            raise ValueError(f"Permiso con ID {permission_id} no existe")
        role_count = self.permission_repo.count_role_permissions(permission_id)
        if role_count > 0:
            raise ValueError(
                f"No se puede eliminar el permiso '{permission.code}' porque est\u00e1 asignado a {role_count} rol(es)"
            )
        self.permission_repo.delete_permission(permission)
        return True

    def search_permissions(self, query_string):
        return self.permission_repo.search(query_string)

    def get_permissions_for_module(self, module_name):
        return self.permission_repo.get_by_module(module_name)
