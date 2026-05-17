"""
PermissionRepository - Acceso a datos para Permission.

Centraliza todas las queries de Permission.
"""

from apps.accounts.models import Permission


class PermissionRepository:
    """
    Repositorio de acceso a datos para Permission.
    """

    @staticmethod
    def get_by_id(permission_id):
        """Obtiene un permiso por ID."""
        try:
            return Permission.objects.get(id=permission_id)
        except Permission.DoesNotExist:
            return None

    @staticmethod
    def get_by_code(code):
        """Obtiene un permiso por code."""
        try:
            return Permission.objects.get(code=code)
        except Permission.DoesNotExist:
            return None

    @staticmethod
    def get_all():
        """Obtiene todos los permisos."""
        return Permission.objects.order_by("code")

    @staticmethod
    def get_by_module(module):
        """Obtiene todos los permisos de un módulo específico."""
        return Permission.objects.filter(module=module).order_by("code")

    @staticmethod
    def create(code, description="", module=""):
        """Crea un nuevo permiso."""
        permission = Permission(
            code=code, description=description, module=module
        )
        permission.save()
        return permission

    @staticmethod
    def create_many(permission_list):
        """
        Crea múltiples permisos desde una lista de dictionaries.

        permission_list: lista de {'code': '...', 'description': '...', 'module': '...'}
        """
        permissions = [
            Permission(
                code=p["code"],
                description=p.get("description", ""),
                module=p.get("module", ""),
            )
            for p in permission_list
        ]
        return Permission.objects.bulk_create(permissions, ignore_conflicts=True)

    @staticmethod
    def update(permission, **kwargs):
        """
        Actualiza un permiso.

        Campos soportados: description, module
        (code no se actualiza: es el identificador único)
        """
        allowed_fields = {"description", "module"}
        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                setattr(permission, key, value)
        permission.save()
        return permission

    @staticmethod
    def delete(permission):
        """
        Elimina un permiso.
        """
        permission.delete()

    @staticmethod
    def search(query_string):
        """
        Búsqueda por code o description (case-insensitive).
        """
        from django.db.models import Q

        return Permission.objects.filter(
            Q(code__icontains=query_string) | Q(description__icontains=query_string)
        ).order_by("code")


"""
RoleRepository - Acceso a datos para Role.

Centraliza todas las queries de Role.
"""

from apps.accounts.models import Role


class RoleRepository:
    """
    Repositorio de acceso a datos para Role.
    """

    @staticmethod
    def get_by_id(role_id):
        """Obtiene un rol por ID."""
        try:
            return Role.objects.prefetch_related("role_permissions__permission").get(
                id=role_id
            )
        except Role.DoesNotExist:
            return None

    @staticmethod
    def get_by_name(name):
        """Obtiene un rol por nombre."""
        try:
            return Role.objects.prefetch_related("role_permissions__permission").get(
                name=name
            )
        except Role.DoesNotExist:
            return None

    @staticmethod
    def get_all_active():
        """Obtiene todos los roles activos."""
        return (
            Role.objects.filter(active=True)
            .prefetch_related("role_permissions__permission")
            .order_by("name")
        )

    @staticmethod
    def get_all():
        """Obtiene todos los roles (activos e inactivos)."""
        return Role.objects.prefetch_related("role_permissions__permission").order_by(
            "name"
        )

    @staticmethod
    def create(name, description="", active=True):
        """Crea un nuevo rol."""
        role = Role(name=name, description=description, active=active)
        role.save()
        return role

    @staticmethod
    def update(role, **kwargs):
        """
        Actualiza un rol con los campos provistos.

        Campos soportados: name, description, active
        """
        allowed_fields = {"name", "description", "active"}
        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                setattr(role, key, value)
        role.save()
        return role

    @staticmethod
    def delete(role):
        """
        Soft-delete (marca como inactivo).
        """
        role.active = False
        role.save()

    @staticmethod
    def get_permissions(role_id):
        """
        Obtiene todos los Permission objects de un rol.
        """
        from apps.accounts.models import Permission

        return Permission.objects.filter(role_permissions__role_id=role_id).distinct()

    @staticmethod
    def add_permission(role, permission):
        """
        Agrega un permiso a un rol via RolePermission.
        """
        from apps.accounts.models import RolePermission

        rp, created = RolePermission.objects.get_or_create(
            role=role, permission=permission
        )
        return rp, created

    @staticmethod
    def remove_permission(role, permission):
        """
        Remueve un permiso de un rol.
        """
        from apps.accounts.models import RolePermission

        return RolePermission.objects.filter(role=role, permission=permission).delete()
