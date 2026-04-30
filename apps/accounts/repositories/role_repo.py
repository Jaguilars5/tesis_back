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

        return Permission.objects.filter(permission_roles__role_id=role_id).distinct()

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
