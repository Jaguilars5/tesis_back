"""
PermissionService - Lógica de negocio para Permission.

Orquesta operaciones para gestionar permisos.
"""

from apps.accounts.repositories.permission_repo import PermissionRepository


class PermissionService:
    """
    Servicio de lógica de negocio para Permission.
    """

    def __init__(self):
        self.permission_repo = PermissionRepository()

    def create_permission(self, code, description="", module=""):
        """
        Crea un nuevo permiso.

        Lanza:
        - ValueError si el code ya existe
        """
        existing = self.permission_repo.get_by_code(code)
        if existing:
            raise ValueError(f"El permiso '{code}' ya existe")

        return self.permission_repo.create(code, description, module)

    def create_permissions_bulk(self, permission_list):
        """
        Crea múltiples permisos desde una lista.

        permission_list: lista de {'code': '...', 'description': '...', 'module': '...'}
        """
        return self.permission_repo.create_many(permission_list)

    def get_permission(self, permission_id):
        """Obtiene un permiso por ID."""
        return self.permission_repo.get_by_id(permission_id)

    def get_permission_by_code(self, code):
        """Obtiene un permiso por code."""
        return self.permission_repo.get_by_code(code)

    def list_permissions(self):
        """Lista todos los permisos."""
        return self.permission_repo.get_all()

    def list_permissions_by_module(self, module):
        """Lista permisos de un módulo específico."""
        return self.permission_repo.get_by_module(module)

    def update_permission(self, permission_id, **kwargs):
        """
        Actualiza un permiso.

        Campos soportados: description, module
        (code no se actualiza: es el identificador único)
        """
        permission = self.permission_repo.get_by_id(permission_id)
        if not permission:
            raise ValueError(f"Permiso con ID {permission_id} no existe")

        return self.permission_repo.update(permission, **kwargs)

    def delete_permission(self, permission_id):
        """
        Elimina un permiso.

        Lanza:
        - ValueError si el permiso está asignado a algún rol o usuario
        """
        from apps.accounts.models import RolePermission, UserPermission

        permission = self.permission_repo.get_by_id(permission_id)
        if not permission:
            raise ValueError(f"Permiso con ID {permission_id} no existe")

        # Verificar si está asignado a roles
        role_count = RolePermission.objects.filter(permission_id=permission_id).count()
        if role_count > 0:
            raise ValueError(
                f"No se puede eliminar el permiso '{permission.code}' porque está asignado a {role_count} rol(es)"
            )

        # Verificar si está asignado a usuarios
        user_count = UserPermission.objects.filter(permission_id=permission_id).count()
        if user_count > 0:
            raise ValueError(
                f"No se puede eliminar el permiso '{permission.code}' porque está asignado a {user_count} usuario(s)"
            )

        self.permission_repo.delete(permission)
        return True

    def search_permissions(self, query_string):
        """
        Búsqueda de permisos por code o description.
        """
        return self.permission_repo.search(query_string)

    def get_permissions_for_module(self, module_name):
        """
        Obtiene todos los permisos de un módulo (ej: 'grading', 'academic').
        Útil para inicializar permisos de una app.
        """
        return self.permission_repo.get_by_module(module_name)
