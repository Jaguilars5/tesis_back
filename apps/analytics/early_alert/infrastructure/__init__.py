__all__ = ["EarlyAlert", "EarlyAlertRepository"]


def __getattr__(name):
    if name == "EarlyAlert":
        from .models import EarlyAlert
        return EarlyAlert
    if name == "EarlyAlertRepository":
        from .repositories import EarlyAlertRepository
        return EarlyAlertRepository
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
