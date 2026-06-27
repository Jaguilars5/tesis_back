"""Capa de infraestructura del modulo IAM."""

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
]


def __getattr__(name):
    if name in ("User", "Role", "Permission", "UserRole", "RolePermission", "UserManager"):
        from .models import User as M, Role as R, Permission as P, UserRole as UR, RolePermission as RP, UserManager as UM
        _map = {"User": M, "Role": R, "Permission": P, "UserRole": UR, "RolePermission": RP, "UserManager": UM}
        return _map[name]
    if name in ("UserRepository", "RoleRepository", "PermissionRepository"):
        from .repositories import UserRepository as UR, RoleRepository as RR, PermissionRepository as PR
        _map = {"UserRepository": UR, "RoleRepository": RR, "PermissionRepository": PR}
        return _map[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
