import importlib


__all__ = [
    "StudentFilter",
]


def __getattr__(name):
    _s = importlib.import_module(".student", __package__)
    _map = {
        "StudentFilter": _s.StudentFilter,
    }
    if name in _map:
        return _map[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
