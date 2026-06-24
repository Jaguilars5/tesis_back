__all__ = [
    "PeriodTypeEntity",
    "PeriodTypeRepositoryInterface",
    "PeriodTypeService",
]


def __getattr__(name):
    if name == "PeriodTypeEntity":
        from .entities import PeriodTypeEntity
        return PeriodTypeEntity
    if name == "PeriodTypeRepositoryInterface":
        from .repositories import PeriodTypeRepositoryInterface
        return PeriodTypeRepositoryInterface
    if name == "PeriodTypeService":
        from .services import PeriodTypeService
        return PeriodTypeService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
