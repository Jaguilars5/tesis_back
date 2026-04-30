"""
RoleService - Lógica de negocio para Role.

Orquesta operaciones entre repositories y modelos.
"""

from apps.accounts.repositories.role_repo import RoleRepository
from apps.accounts.repositories.permission_repo import PermissionRepository


class RoleService:
    """
    Servicio de lógica de negocio para Role.
    """

    def __init__(self):
        self.role_repo = RoleRepository()
        self.permission_repo = PermissionRepository()

    def create_role(self, name, description="", active=True):
        """
        Crea un nuevo rol.

        Lanza:
        - ValueError si el nombre ya existe
        """
        existing = self.role_repo.get_by_name(name)
        if existing:
            raise ValueError(f"El rol '{name}' ya existe")

        return self.role_repo.create(name, description, active)

    def get_role(self, role_id):
        """Obtiene un rol por ID."""
        return self.role_repo.get_by_id(role_id)

    def get_role_by_name(self, name):
        """Obtiene un rol por nombre."""
        return self.role_repo.get_by_name(name)

    def list_roles(self, only_active=True):
        """Lista todos los roles."""
        if only_active:
            return self.role_repo.get_all_active()
        return self.role_repo.get_all()

    def update_role(self, role_id, **kwargs):
        """
        Actualiza un rol.

        Campos soportados: name, description, active
        """
        role = self.role_repo.get_by_id(role_id)
        if not role:
            raise ValueError(f"Rol con ID {role_id} no existe")

        # Si se actualiza name, verificar que no esté duplicado
        if "name" in kwargs and kwargs["name"] != role.name:
            existing = self.role_repo.get_by_name(kwargs["name"])
            if existing:
                raise ValueError(f"El rol '{kwargs['name']}' ya existe")

        return self.role_repo.update(role, **kwargs)

    def deactivate_role(self, role_id):
        """Desactiva un rol (soft-delete)."""
        role = self.role_repo.get_by_id(role_id)
        if not role:
            raise ValueError(f"Rol con ID {role_id} no existe")

        # Verificar si hay usuarios activos con este rol
        from apps.accounts.models import User

        active_users = User.objects.filter(role_id=role_id, active=True).count()
        if active_users > 0:
            raise ValueError(
                f"No se puede desactivar el rol '{role.name}' porque hay {active_users} usuarios activos asignados"
            )

        self.role_repo.delete(role)
        return role

    def get_role_permissions(self, role_id):
        """Obtiene todos los permisos de un rol."""
        return self.role_repo.get_permissions(role_id)

    def add_permission_to_role(self, role_id, permission_codename):
        """
        Agrega un permiso a un rol.

        Lanza:
        - ValueError si el rol o permiso no existe
        """
        role = self.role_repo.get_by_id(role_id)
        if not role:
            raise ValueError(f"Rol con ID {role_id} no existe")

        permission = self.permission_repo.get_by_codename(permission_codename)
        if not permission:
            raise ValueError(f"El permiso {permission_codename} no existe")

        rp, created = self.role_repo.add_permission(role, permission)
        return rp, created

    def remove_permission_from_role(self, role_id, permission_codename):
        """
        Remueve un permiso de un rol.
        """
        role = self.role_repo.get_by_id(role_id)
        if not role:
            raise ValueError(f"Rol con ID {role_id} no existe")

        permission = self.permission_repo.get_by_codename(permission_codename)
        if not permission:
            raise ValueError(f"El permiso {permission_codename} no existe")

        deleted_count, _ = self.role_repo.remove_permission(role, permission)
        return deleted_count > 0

    def assign_permissions_to_role(self, role_id, permission_codenames):
        """
        Asigna múltiples permisos a un rol de una sola vez.

        Reemplaza los permisos existentes con los nuevos.
        """
        from apps.accounts.models import RolePermission

        role = self.role_repo.get_by_id(role_id)
        if not role:
            raise ValueError(f"Rol con ID {role_id} no existe")

        # Obtener permiso objects
        permissions = self.permission_repo.get_all()
        permission_dict = {p.codename: p for p in permissions}

        # Validar que todos los codenames existan
        for codename in permission_codenames:
            if codename not in permission_dict:
                raise ValueError(f"El permiso {codename} no existe")

        # Limpiar permisos actuales y asignar nuevos
        RolePermission.objects.filter(role_id=role_id).delete()

        permission_objs = [permission_dict[c] for c in permission_codenames]
        rps = [RolePermission(role=role, permission=p) for p in permission_objs]
        RolePermission.objects.bulk_create(rps)

        return len(rps)
