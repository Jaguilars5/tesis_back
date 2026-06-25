"""Capa de aplicación del bounded context academic_period."""

__all__ = ["AcademicPeriodSerializer", "run_all_validators"]


def __getattr__(name):
    if name == "AcademicPeriodSerializer":
        from .serializers import AcademicPeriodSerializer
        return AcademicPeriodSerializer
    if name == "run_all_validators":
        from .validators import run_all_validators
        return run_all_validators
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
