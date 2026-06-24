"""Capa de dominio - interfaces de repositorio."""

__all__ = [
    "UserRepositoryInterface",
    "RoleRepositoryInterface",
    "PermissionRepositoryInterface",
]


def __getattr__(name):
    if name == "UserRepositoryInterface":
        from .repositories import UserRepositoryInterface
        return UserRepositoryInterface
    if name == "RoleRepositoryInterface":
        from .repositories import RoleRepositoryInterface
        return RoleRepositoryInterface
    if name == "PermissionRepositoryInterface":
        from .repositories import PermissionRepositoryInterface
        return PermissionRepositoryInterface
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
