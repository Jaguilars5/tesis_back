__all__ = ["PeriodType", "PeriodTypeRepository"]


def __getattr__(name):
    if name == "PeriodType":
        from .models import PeriodType
        return PeriodType
    if name == "PeriodTypeRepository":
        from .repositories import PeriodTypeRepository
        return PeriodTypeRepository
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
