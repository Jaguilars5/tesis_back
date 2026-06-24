__all__ = [
    "Severity",
    "SeverityRepository",
    "SeverityService",
]

def __getattr__(name):
    if name == "Severity":
        from .infrastructure.models import Severity
        return Severity
    if name == "SeverityRepository":
        from .infrastructure.repositories import SeverityRepository
        return SeverityRepository
    if name == "SeverityService":
        from .domain.services import SeverityService
        return SeverityService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
