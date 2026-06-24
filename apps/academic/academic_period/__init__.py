"""Submódulo bounded context: academic_period."""

__all__ = [
    "AcademicPeriod",
    "AcademicPeriodRepository",
    "AcademicPeriodService",
]


def __getattr__(name):
    if name == "AcademicPeriod":
        from .infrastructure.models import AcademicPeriod

        return AcademicPeriod
    if name == "AcademicPeriodRepository":
        from .infrastructure.repositories import AcademicPeriodRepository

        return AcademicPeriodRepository
    if name == "AcademicPeriodService":
        from .domain.services import AcademicPeriodService

        return AcademicPeriodService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
