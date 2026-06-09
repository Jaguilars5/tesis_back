from apps.iam.repositories.role_repo import RoleRepository
from apps.iam.repositories.permission_repo import PermissionRepository
from apps.iam.repositories.user_repo import UserRepository


class RoleService:
    def __init__(self):
        self.role_repo = RoleRepository()
        self.permission_repo = PermissionRepository()

    def create_role(self, name, description="", active=True):
        existing = self.role_repo.get_by_name(name)
        if existing:
            raise ValueError(f"El rol '{name}' ya existe")

        return self.role_repo.create(name, description, active)

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

        return self.role_repo.update(role, **kwargs)

    def deactivate_role(self, role_id):
        role = self.role_repo.get_by_id(role_id)
        if not role:
            raise ValueError(f"Rol con ID {role_id} no existe")

        active_users = len(UserRepository.get_by_role(role_id))
        if active_users > 0:
            raise ValueError(
                f"No se puede desactivar el rol '{role.name}' porque hay {active_users} usuarios activos asignados"
            )

        self.role_repo.delete(role)
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
