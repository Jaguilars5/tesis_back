__all__ = ["ClassSchedule", "DayOfWeekChoices", "ClassScheduleRepository"]


def __getattr__(name):
    if name == "ClassSchedule":
        from .models import ClassSchedule
        return ClassSchedule
    if name == "DayOfWeekChoices":
        from .models import DayOfWeekChoices
        return DayOfWeekChoices
    if name == "ClassScheduleRepository":
        from .repositories import ClassScheduleRepository
        return ClassScheduleRepository
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
