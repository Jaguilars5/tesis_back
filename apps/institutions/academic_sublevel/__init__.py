__all__ = [
    "AcademicSublevel",
    "AcademicSublevelRepository",
    "AcademicSublevelService",
]

def __getattr__(name):
    if name == "AcademicSublevel":
        from .infrastructure.models import AcademicSublevel
        return AcademicSublevel
    if name == "AcademicSublevelRepository":
        from .infrastructure.repositories import AcademicSublevelRepository
        return AcademicSublevelRepository
    if name == "AcademicSublevelService":
        from .domain.services import AcademicSublevelService
        return AcademicSublevelService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
