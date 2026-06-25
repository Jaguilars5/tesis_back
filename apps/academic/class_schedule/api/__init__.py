__all__ = ["ClassScheduleViewSet"]


def __getattr__(name):
    if name == "ClassScheduleViewSet":
        from .views import ClassScheduleViewSet
        return ClassScheduleViewSet
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
