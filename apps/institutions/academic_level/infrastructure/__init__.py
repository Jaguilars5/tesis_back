__all__ = ["AcademicLevel", "AcademicLevelRepository"]


def __getattr__(name):
    if name == "AcademicLevel":
        from .models import AcademicLevel
        return AcademicLevel
    if name == "AcademicLevelRepository":
        from .repositories import AcademicLevelRepository
        return AcademicLevelRepository
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
