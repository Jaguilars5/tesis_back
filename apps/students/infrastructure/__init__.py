import importlib


__all__ = [
    "Student",
    "StudentRepresentative",
    "Enrollment",
    "WithdrawalReason",
    "SpecialNeedsType",
    "Kinship",
    "EnrollmentStatusChoices",
    "StudentRepository",
    "StudentRepresentativeRepository",
    "EnrollmentRepository",
]


def __getattr__(name):
    _m = importlib.import_module(".models", __package__)
    _r = importlib.import_module(".repositories", __package__)
    _map = {
        "Student": _m.Student,
        "StudentRepresentative": _m.StudentRepresentative,
        "Enrollment": _m.Enrollment,
        "WithdrawalReason": _m.WithdrawalReason,
        "SpecialNeedsType": _m.SpecialNeedsType,
        "Kinship": _m.Kinship,
        "EnrollmentStatusChoices": _m.EnrollmentStatusChoices,
        "StudentRepository": _r.StudentRepository,
        "StudentRepresentativeRepository": _r.StudentRepresentativeRepository,
        "EnrollmentRepository": _r.EnrollmentRepository,
    }
    if name in _map:
        return _map[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
