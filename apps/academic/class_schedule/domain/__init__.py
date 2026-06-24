__all__ = [
    "ClassScheduleEntity",
    "ClassScheduleRepositoryInterface",
    "ClassScheduleService",
]


def __getattr__(name):
    if name == "ClassScheduleEntity":
        from .entities import ClassScheduleEntity
        return ClassScheduleEntity
    if name == "ClassScheduleRepositoryInterface":
        from .repositories import ClassScheduleRepositoryInterface
        return ClassScheduleRepositoryInterface
    if name == "ClassScheduleService":
        from .services import ClassScheduleService
        return ClassScheduleService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
