from django.contrib.auth.password_validation import validate_password

from ..infrastructure.repositories import (
    UserRepository,
    RoleRepository,
    PermissionRepository,
)


class UserService:
    repository = UserRepository

    @classmethod
    def create_user(cls, document_number, names, last_names, email, password, role_id,
                    birth_date=None, phone="", document_type_id=None, parish_id=None):
        existing_email = cls.repository.get_by_email(email)
        if existing_email:
            raise ValueError(f"El email {email} ya está registrado")

        existing_dni = cls.repository.get_by_dni(document_number)
        if existing_dni:
            raise ValueError(f"El DNI {document_number} ya está registrado")

        role = RoleRepository.get_by_id(role_id)
        if not role:
            raise ValueError(f"El rol con ID {role_id} no existe")

        return cls.repository.create_user_with_person(
            document_number=document_number,
            names=names,
            last_names=last_names,
            email=email,
            password=password,
            role_id=role_id,
            birth_date=birth_date,
            phone=phone,
            document_type_id=document_type_id,
            parish_id=parish_id,
        )

    @classmethod
    def get_user(cls, user_id):
        user = cls.repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"Usuario con ID {user_id} no existe")
        return user

    @classmethod
    def get_user_by_email(cls, email):
        return cls.repository.get_by_email(email)

    @classmethod
    def get_user_by_username(cls, username):
        return cls.repository.get_by_username(username)

    @classmethod
    def list_users(cls):
        return cls.repository.get_all_active()

    @classmethod
    def list_users_by_role(cls, role_id):
        return cls.repository.get_by_role(role_id)

    @classmethod
    def list_users_by_role_code(cls, code):
        return cls.repository.get_by_role_code(code)

    @classmethod
    def update_user(cls, user_id, **kwargs):
        user = cls.repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"Usuario con ID {user_id} no existe")
        current_email = user.person.email if user.person else None
        if "email" in kwargs and kwargs["email"] != current_email:
            existing = cls.repository.get_by_email(kwargs["email"])
            if existing and existing.id != user.id:
                raise ValueError(f"El email {kwargs['email']} ya está registrado")
        if "role" in kwargs:
            role = RoleRepository.get_by_id(kwargs["role"])
            if not role:
                raise ValueError(f"El rol con ID {kwargs['role']} no existe")
        return cls.repository.update_user(user, **kwargs)

    @classmethod
    def change_password(cls, user_id, new_password):
        user = cls.repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"Usuario con ID {user_id} no existe")
        validate_password(new_password, user=user)
        return cls.repository.change_password(user, new_password)

    @classmethod
    def deactivate_user(cls, user_id):
        user = cls.repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"Usuario con ID {user_id} no existe")
        cls.repository.delete_user(user)
        return user

    @classmethod
    def has_permission(cls, user_id, permission_code):
        user = cls.repository.get_by_id(user_id)
        if not user:
            return False
        return user.has_perm(permission_code)

    @classmethod
    def get_user_permissions(cls, user_id):
        user = cls.repository.get_by_id(user_id)
        if not user:
            return set()
        return user.get_all_permissions()

    @classmethod
    def search_users(cls, query_string):
        return cls.repository.search(query_string)

    @classmethod
    def search_users_by_role_code(cls, role_code, search=None):
        return cls.repository.search_by_role_code(role_code, search=search)


class RoleService:
    repository = RoleRepository

    @classmethod
    def create_role(cls, name, description="", active=True):
        existing = cls.repository.get_by_name(name)
        if existing:
            raise ValueError(f"El rol '{name}' ya existe")
        return cls.repository.create_role(name, description, active)

    @classmethod
    def get_role(cls, role_id):
        role = cls.repository.get_by_id(role_id)
        if not role:
            raise ValueError(f"Rol con ID {role_id} no existe")
        return role

    @classmethod
    def get_role_by_name(cls, name):
        return cls.repository.get_by_name(name)

    @classmethod
    def list_roles(cls, only_active=True):
        if only_active:
            return cls.repository.get_all_active()
        return cls.repository.get_all()

    @classmethod
    def update_role(cls, role_id, **kwargs):
        role = cls.repository.get_by_id(role_id)
        if not role:
            raise ValueError(f"Rol con ID {role_id} no existe")
        if "name" in kwargs and kwargs["name"] != role.name:
            existing = cls.repository.get_by_name(kwargs["name"])
            if existing:
                raise ValueError(f"El rol '{kwargs['name']}' ya existe")
        return cls.repository.update_role(role, **kwargs)

    @classmethod
    def deactivate_role(cls, role_id):
        role = cls.repository.get_by_id(role_id)
        if not role:
            raise ValueError(f"Rol con ID {role_id} no existe")
        active_users = len(UserRepository.get_by_role(role_id))
        if active_users > 0:
            raise ValueError(
                f"No se puede desactivar el rol '{role.name}' porque hay {active_users} usuarios activos asignados"
            )
        cls.repository.delete_role(role)
        return role

    @classmethod
    def soft_delete(cls, pk, confirm=False):
        role = cls.repository.get_by_id(pk)
        if not role:
            raise ValueError(f"Rol con ID {pk} no existe")
        counts = cls.repository.get_cascade_counts(pk)
        total = sum(counts.values())

        if total > 0 and not confirm:
            parts = [f"{v} {k}" for k, v in counts.items()]
            return {
                "requires_confirmation": True,
                "affected_records": total,
                "message": f"Esta acción desactivará {', '.join(parts)} relacionados",
                "id": role.id,
                "is_active": True,
            }

        total = cls.repository.deactivate_cascade(pk)
        return {
            "id": role.id,
            "is_active": False,
            "deactivated_records": total,
        }

    @classmethod
    def get_role_permissions(cls, role_id):
        return cls.repository.get_permissions(role_id)

    @classmethod
    def add_permission_to_role(cls, role_id, permission_code):
        role = cls.repository.get_by_id(role_id)
        if not role:
            raise ValueError(f"Rol con ID {role_id} no existe")
        permission = PermissionRepository.get_by_code(permission_code)
        if not permission:
            raise ValueError(f"El permiso {permission_code} no existe")
        rp, created = cls.repository.add_permission(role, permission)
        return rp, created

    @classmethod
    def remove_permission_from_role(cls, role_id, permission_code):
        role = cls.repository.get_by_id(role_id)
        if not role:
            raise ValueError(f"Rol con ID {role_id} no existe")
        permission = PermissionRepository.get_by_code(permission_code)
        if not permission:
            raise ValueError(f"El permiso {permission_code} no existe")
        deleted_count, _ = cls.repository.remove_permission(role, permission)
        return deleted_count > 0

    @classmethod
    def assign_permissions_to_role(cls, role_id, permission_codes):
        role = cls.repository.get_by_id(role_id)
        if not role:
            raise ValueError(f"Rol con ID {role_id} no existe")
        permissions = PermissionRepository.get_all()
        permission_dict = {p.code: p for p in permissions}
        for code in permission_codes:
            if code not in permission_dict:
                raise ValueError(f"El permiso {code} no existe")
        permission_objs = [permission_dict[c] for c in permission_codes]
        cls.repository.set_permissions(role, permission_objs)
        return len(permission_objs)


class PermissionService:
    repository = PermissionRepository

    @classmethod
    def create_permission(cls, code, description="", module=""):
        existing = cls.repository.get_by_code(code)
        if existing:
            raise ValueError(f"El permiso '{code}' ya existe")
        return cls.repository.create_permission(code, description, module)

    @classmethod
    def create_permissions_bulk(cls, permission_list):
        return cls.repository.create_many(permission_list)

    @classmethod
    def get_permission(cls, permission_id):
        permission = cls.repository.get_by_id(permission_id)
        if not permission:
            raise ValueError(f"Permiso con ID {permission_id} no existe")
        return permission

    @classmethod
    def get_permission_by_code(cls, code):
        return cls.repository.get_by_code(code)

    @classmethod
    def list_permissions(cls):
        return cls.repository.get_all()

    @classmethod
    def list_permissions_by_module(cls, module):
        return cls.repository.get_by_module(module)

    @classmethod
    def update_permission(cls, permission_id, **kwargs):
        permission = cls.repository.get_by_id(permission_id)
        if not permission:
            raise ValueError(f"Permiso con ID {permission_id} no existe")
        return cls.repository.update_permission(permission, **kwargs)

    @classmethod
    def delete_permission(cls, permission_id):
        permission = cls.repository.get_by_id(permission_id)
        if not permission:
            raise ValueError(f"Permiso con ID {permission_id} no existe")
        role_count = cls.repository.count_role_permissions(permission_id)
        if role_count > 0:
            raise ValueError(
                f"No se puede eliminar el permiso '{permission.code}' porque está asignado a {role_count} rol(es)"
            )
        cls.repository.delete_permission(permission)
        return True

    @classmethod
    def search_permissions(cls, query_string):
        return cls.repository.search(query_string)

    @classmethod
    def get_permissions_for_module(cls, module_name):
        return cls.repository.get_by_module(module_name)
