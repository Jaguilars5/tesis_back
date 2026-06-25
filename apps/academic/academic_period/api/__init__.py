"""Capa de API del bounded context academic_period."""

__all__ = ["AcademicPeriodViewSet"]


def __getattr__(name):
    if name == "AcademicPeriodViewSet":
        from .views import AcademicPeriodViewSet
        return AcademicPeriodViewSet
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
