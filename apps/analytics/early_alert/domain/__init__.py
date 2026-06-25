__all__ = ["EarlyAlertRepositoryInterface", "EarlyAlertService"]


def __getattr__(name):
    if name == "EarlyAlertRepositoryInterface":
        from .repositories import EarlyAlertRepositoryInterface
        return EarlyAlertRepositoryInterface
    if name == "EarlyAlertService":
        from .services import EarlyAlertService
        return EarlyAlertService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
