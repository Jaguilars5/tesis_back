"""Capa de dominio del bounded context academic_sublevel."""

__all__ = [
    "AcademicSublevelEntity",
    "AcademicSublevelRepositoryInterface",
    "AcademicSublevelService",
]


def __getattr__(name):
    if name == "AcademicSublevelEntity":
        from .entities import AcademicSublevelEntity
        return AcademicSublevelEntity
    if name == "AcademicSublevelRepositoryInterface":
        from .repositories import AcademicSublevelRepositoryInterface
        return AcademicSublevelRepositoryInterface
    if name == "AcademicSublevelService":
        from .services import AcademicSublevelService
        return AcademicSublevelService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
