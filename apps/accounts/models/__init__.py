"""
Re-exporta todos los modelos del módulo accounts.

Permite usar:
    from apps.accounts.models import User, Role, Permission, ...
en lugar de:
    from apps.accounts.models.user import User
    from apps.accounts.models.role import Role
"""

from .user import User
from .person import Person
from .user_role import UserRole
from .role import Role
from .permission import Permission
from .role_permission import RolePermission
from .user_permission import UserPermission

__all__ = [
    "User",
    "Person",
    "UserRole",
    "Role",
    "Permission",
    "RolePermission",
    "UserPermission",
]
