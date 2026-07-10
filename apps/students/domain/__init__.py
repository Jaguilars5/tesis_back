import importlib


__all__ = [
    "StudentRepositoryInterface",
    "StudentRepresentativeRepositoryInterface",
    "EnrollmentRepositoryInterface",
    "StudentService",
    "EnrollmentService",
]


def __getattr__(name):
    _r = importlib.import_module(".repositories", __package__)
    _s = importlib.import_module(".services", __package__)
    _map = {
        "StudentRepositoryInterface": _r.StudentRepositoryInterface,
        "StudentRepresentativeRepositoryInterface": _r.StudentRepresentativeRepositoryInterface,
        "EnrollmentRepositoryInterface": _r.EnrollmentRepositoryInterface,
        "StudentService": _s.StudentService,
        "EnrollmentService": _s.EnrollmentService,
    }
    if name in _map:
        return _map[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
