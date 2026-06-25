__all__ = [
    "ClassScheduleRepositoryInterface",
    "ClassScheduleService",
]


def __getattr__(name):
    if name == "ClassScheduleRepositoryInterface":
        from .repositories import ClassScheduleRepositoryInterface
        return ClassScheduleRepositoryInterface
    if name == "ClassScheduleService":
        from .services import ClassScheduleService
        return ClassScheduleService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
