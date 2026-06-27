"""Capa de dominio del modulo IAM."""

__all__ = [
    "UserEntity",
    "RoleEntity",
    "PermissionEntity",
    "UserRoleEntity",
    "RolePermissionEntity",
]


def __getattr__(name):
    if name == "UserEntity":
        from .entities import UserEntity
        return UserEntity
    if name == "RoleEntity":
        from .entities import RoleEntity
        return RoleEntity
    if name == "PermissionEntity":
        from .entities import PermissionEntity
        return PermissionEntity
    if name == "UserRoleEntity":
        from .entities import UserRoleEntity
        return UserRoleEntity
    if name == "RolePermissionEntity":
        from .entities import RolePermissionEntity
        return RolePermissionEntity
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
