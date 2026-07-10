import importlib


__all__ = [
    "StudentSerializer",
    "StudentDetailSerializer",
    "StudentCreateSerializer",
    "StudentRepresentativeSerializer",
    "EnrollmentSerializer",
    "EnrollmentCreateSerializer",
    "KinshipSerializer",
    "SpecialNeedsTypeSerializer",
]


def __getattr__(name):
    _s = importlib.import_module("...application.serializers", __package__)
    _map = {
        "StudentSerializer": _s.StudentSerializer,
        "StudentDetailSerializer": _s.StudentDetailSerializer,
        "StudentCreateSerializer": _s.StudentCreateSerializer,
        "StudentRepresentativeSerializer": _s.StudentRepresentativeSerializer,
        "EnrollmentSerializer": _s.EnrollmentSerializer,
        "EnrollmentCreateSerializer": _s.EnrollmentCreateSerializer,
        "KinshipSerializer": _s.KinshipSerializer,
        "SpecialNeedsTypeSerializer": _s.SpecialNeedsTypeSerializer,
    }
    if name in _map:
        return _map[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
