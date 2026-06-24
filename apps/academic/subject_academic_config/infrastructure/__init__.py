__all__ = ["SubjectAcademicConfig", "SubjectAcademicConfigRepository"]


def __getattr__(name):
    if name == "SubjectAcademicConfig":
        from .models import SubjectAcademicConfig
        return SubjectAcademicConfig
    if name == "SubjectAcademicConfigRepository":
        from .repositories import SubjectAcademicConfigRepository
        return SubjectAcademicConfigRepository
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
