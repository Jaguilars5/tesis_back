__all__ = [
    "PeriodType",
    "PeriodTypeRepository",
    "PeriodTypeService",
]


def __getattr__(name):
    if name == "PeriodType":
        from .infrastructure.models import PeriodType
        return PeriodType
    if name == "PeriodTypeRepository":
        from .infrastructure.repositories import PeriodTypeRepository
        return PeriodTypeRepository
    if name == "PeriodTypeService":
        from .domain.services import PeriodTypeService
        return PeriodTypeService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
