__all__ = ["ClassScheduleSerializer", "run_all_validators"]


def __getattr__(name):
    if name == "ClassScheduleSerializer":
        from .serializers import ClassScheduleSerializer
        return ClassScheduleSerializer
    if name == "run_all_validators":
        from .validators import run_all_validators
        return run_all_validators
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
