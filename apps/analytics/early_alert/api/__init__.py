__all__ = ["EarlyAlertViewSet"]


def __getattr__(name):
    if name == "EarlyAlertViewSet":
        from .views import EarlyAlertViewSet
        return EarlyAlertViewSet
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
