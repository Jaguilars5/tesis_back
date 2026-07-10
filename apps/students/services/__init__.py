import importlib


__all__ = ["EnrollmentService", "StudentService"]


def __getattr__(name):
    _s = importlib.import_module("..domain.services", __package__)
    _map = {
        "EnrollmentService": _s.EnrollmentService,
        "StudentService": _s.StudentService,
    }
    if name in _map:
        return _map[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
