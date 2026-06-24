"""
M\u00f3dulo de Identidad, Acceso y Gesti\u00f3n de Usuarios (IAM).
"""

__all__ = [
    "User",
    "Role",
    "Permission",
    "UserRole",
    "RolePermission",
    "UserManager",
    "UserRepository",
    "RoleRepository",
    "PermissionRepository",
    "UserService",
    "RoleService",
    "PermissionService",
]


def __getattr__(name):
    if name in ("User", "Role", "Permission", "UserRole", "RolePermission", "UserManager"):
        from .models import User as M, Role as R, Permission as P, UserRole as UR, RolePermission as RP, UserManager as UM
        _map = {"User": M, "Role": R, "Permission": P, "UserRole": UR, "RolePermission": RP, "UserManager": UM}
        return _map[name]
    if name in ("UserRepository", "RoleRepository", "PermissionRepository"):
        from .infrastructure.repositories import UserRepository, RoleRepository, PermissionRepository
        _map = {"UserRepository": UserRepository, "RoleRepository": RoleRepository, "PermissionRepository": PermissionRepository}
        return _map[name]
    if name in ("UserService", "RoleService", "PermissionService"):
        from .domain.services import UserService, RoleService, PermissionService
        _map = {"UserService": UserService, "RoleService": RoleService, "PermissionService": PermissionService}
        return _map[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
