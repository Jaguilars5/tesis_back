"""Capa de infraestructura del submódulo academic_period."""

__all__ = ["AcademicPeriod", "AcademicPeriodRepository"]


def __getattr__(name):
    if name == "AcademicPeriod":
        from .models import AcademicPeriod
        return AcademicPeriod
    if name == "AcademicPeriodRepository":
        from .repositories import AcademicPeriodRepository
        return AcademicPeriodRepository
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
