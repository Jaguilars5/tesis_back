import importlib


__all__ = [
    "Student",
    "StudentRepresentative",
    "Enrollment",
    "WithdrawalReason",
    "SpecialNeedsType",
    "Kinship",
    "EnrollmentStatusChoices",
]


def __getattr__(name):
    _m = importlib.import_module("..infrastructure.models", __package__)
    _map = {
        "Student": _m.Student,
        "StudentRepresentative": _m.StudentRepresentative,
        "Enrollment": _m.Enrollment,
        "WithdrawalReason": _m.WithdrawalReason,
        "SpecialNeedsType": _m.SpecialNeedsType,
        "Kinship": _m.Kinship,
        "EnrollmentStatusChoices": _m.EnrollmentStatusChoices,
    }
    if name in _map:
        return _map[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
