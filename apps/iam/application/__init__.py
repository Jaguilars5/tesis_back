"""Capa de aplicaci\u00f3n del m\u00f3dulo IAM."""

__all__ = [
    "UserLoginDataSerializer",
    "LoginResponseSerializer",
    "TokenRefreshResponseSerializer",
    "CustomTokenRefreshSerializer",
    "LoginSerializer",
    "PermissionSerializer",
    "RolePermissionSerializer",
    "RoleListSerializer",
    "RoleDetailSerializer",
    "UserListSerializer",
    "UserDetailSerializer",
    "UserCreateSerializer",
]


def __getattr__(name):
    from . import serializers as _s

    _map = {
        "UserLoginDataSerializer": _s.UserLoginDataSerializer,
        "LoginResponseSerializer": _s.LoginResponseSerializer,
        "TokenRefreshResponseSerializer": _s.TokenRefreshResponseSerializer,
        "CustomTokenRefreshSerializer": _s.CustomTokenRefreshSerializer,
        "LoginSerializer": _s.LoginSerializer,
        "PermissionSerializer": _s.PermissionSerializer,
        "RolePermissionSerializer": _s.RolePermissionSerializer,
        "RoleListSerializer": _s.RoleListSerializer,
        "RoleDetailSerializer": _s.RoleDetailSerializer,
        "UserListSerializer": _s.UserListSerializer,
        "UserDetailSerializer": _s.UserDetailSerializer,
        "UserCreateSerializer": _s.UserCreateSerializer,
    }
    if name in _map:
        return _map[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
