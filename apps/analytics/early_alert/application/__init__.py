__all__ = ["EarlyAlertSerializer"]


def __getattr__(name):
    if name == "EarlyAlertSerializer":
        from .serializers import EarlyAlertSerializer
        return EarlyAlertSerializer
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
