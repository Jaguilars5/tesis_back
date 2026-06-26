__all__ = ["SchoolYear", "SchoolYearRepository"]


def __getattr__(name):
    if name == "SchoolYear":
        from .models import SchoolYear
        return SchoolYear
    if name == "SchoolYearRepository":
        from .repositories import SchoolYearRepository
        return SchoolYearRepository
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
