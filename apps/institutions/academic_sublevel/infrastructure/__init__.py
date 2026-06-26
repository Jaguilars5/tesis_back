__all__ = ["AcademicSublevel", "AcademicSublevelRepository"]


def __getattr__(name):
    if name == "AcademicSublevel":
        from .models import AcademicSublevel
        return AcademicSublevel
    if name == "AcademicSublevelRepository":
        from .repositories import AcademicSublevelRepository
        return AcademicSublevelRepository
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
