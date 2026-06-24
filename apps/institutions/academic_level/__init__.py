__all__ = [
    "AcademicLevel",
    "AcademicLevelRepository",
    "AcademicLevelService",
]

def __getattr__(name):
    if name == "AcademicLevel":
        from .infrastructure.models import AcademicLevel
        return AcademicLevel
    if name == "AcademicLevelRepository":
        from .infrastructure.repositories import AcademicLevelRepository
        return AcademicLevelRepository
    if name == "AcademicLevelService":
        from .domain.services import AcademicLevelService
        return AcademicLevelService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
