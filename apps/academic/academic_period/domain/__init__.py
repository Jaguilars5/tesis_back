"""Capa de dominio del bounded context academic_period."""

__all__ = [
    "AcademicPeriodEntity",
    "AcademicPeriodRepositoryInterface",
    "AcademicPeriodService",
]


def __getattr__(name):
    if name == "AcademicPeriodEntity":
        from .entities import AcademicPeriodEntity

        return AcademicPeriodEntity
    if name == "AcademicPeriodRepositoryInterface":
        from .repositories import AcademicPeriodRepositoryInterface

        return AcademicPeriodRepositoryInterface
    if name == "AcademicPeriodService":
        from .services import AcademicPeriodService

        return AcademicPeriodService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
