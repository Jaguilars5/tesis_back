__all__ = ["EarlyAlert", "EarlyAlertRepository", "EarlyAlertService"]


def __getattr__(name):
    if name == "EarlyAlert":
        from .infrastructure.models import EarlyAlert
        return EarlyAlert
    if name == "EarlyAlertRepository":
        from .infrastructure.repositories import EarlyAlertRepository
        return EarlyAlertRepository
    if name == "EarlyAlertService":
        from .domain.services import EarlyAlertService
        return EarlyAlertService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
