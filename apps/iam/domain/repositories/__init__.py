import importlib


__all__ = [
    "UserRepositoryInterface",
    "RoleRepositoryInterface",
    "PermissionRepositoryInterface",
]


def __getattr__(name):
    _m = importlib.import_module(".interfaces", __package__)
    _map = {
        "UserRepositoryInterface": _m.UserRepositoryInterface,
        "RoleRepositoryInterface": _m.RoleRepositoryInterface,
        "PermissionRepositoryInterface": _m.PermissionRepositoryInterface,
    }
    if name in _map:
        return _map[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
