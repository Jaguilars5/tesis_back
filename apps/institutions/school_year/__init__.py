__all__ = [
    "SchoolYear",
    "SchoolYearRepository",
    "SchoolYearService",
]

def __getattr__(name):
    if name == "SchoolYear":
        from .infrastructure.models import SchoolYear
        return SchoolYear
    if name == "SchoolYearRepository":
        from .infrastructure.repositories import SchoolYearRepository
        return SchoolYearRepository
    if name == "SchoolYearService":
        from .domain.services import SchoolYearService
        return SchoolYearService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
