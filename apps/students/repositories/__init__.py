import importlib


__all__ = [
    "EnrollmentRepository",
    "StudentRepository",
    "StudentRepresentativeRepository",
]


def __getattr__(name):
    _r = importlib.import_module("..infrastructure.repositories", __package__)
    _map = {
        "EnrollmentRepository": _r.EnrollmentRepository,
        "StudentRepository": _r.StudentRepository,
        "StudentRepresentativeRepository": _r.StudentRepresentativeRepository,
    }
    if name in _map:
        return _map[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
