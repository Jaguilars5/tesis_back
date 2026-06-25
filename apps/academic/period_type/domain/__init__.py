__all__ = [
    "PeriodTypeRepositoryInterface",
    "PeriodTypeService",
]


def __getattr__(name):
    if name == "PeriodTypeRepositoryInterface":
        from .repositories import PeriodTypeRepositoryInterface
        return PeriodTypeRepositoryInterface
    if name == "PeriodTypeService":
        from .services import PeriodTypeService
        return PeriodTypeService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
