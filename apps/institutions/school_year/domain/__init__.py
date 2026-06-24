"""Capa de dominio del bounded context school_year."""

__all__ = [
    "SchoolYearEntity",
    "SchoolYearRepositoryInterface",
    "SchoolYearService",
]


def __getattr__(name):
    if name == "SchoolYearEntity":
        from .entities import SchoolYearEntity
        return SchoolYearEntity
    if name == "SchoolYearRepositoryInterface":
        from .repositories import SchoolYearRepositoryInterface
        return SchoolYearRepositoryInterface
    if name == "SchoolYearService":
        from .services import SchoolYearService
        return SchoolYearService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
