"""Capa de dominio del bounded context academic_level."""

__all__ = [
    "AcademicLevelEntity",
    "AcademicLevelRepositoryInterface",
    "AcademicLevelService",
]


def __getattr__(name):
    if name == "AcademicLevelEntity":
        from .entities import AcademicLevelEntity
        return AcademicLevelEntity
    if name == "AcademicLevelRepositoryInterface":
        from .repositories import AcademicLevelRepositoryInterface
        return AcademicLevelRepositoryInterface
    if name == "AcademicLevelService":
        from .services import AcademicLevelService
        return AcademicLevelService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
