__all__ = [
    "ClassSchedule",
    "DayOfWeekChoices",
    "ClassScheduleRepository",
    "ClassScheduleService",
]


def __getattr__(name):
    if name == "ClassSchedule":
        from .infrastructure.models import ClassSchedule
        return ClassSchedule
    if name == "DayOfWeekChoices":
        from .infrastructure.models import DayOfWeekChoices
        return DayOfWeekChoices
    if name == "ClassScheduleRepository":
        from .infrastructure.repositories import ClassScheduleRepository
        return ClassScheduleRepository
    if name == "ClassScheduleService":
        from .domain.services import ClassScheduleService
        return ClassScheduleService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
