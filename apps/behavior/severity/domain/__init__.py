"""Capa de dominio del bounded context severity."""

__all__ = [
    "SeverityEntity",
    "SeverityRepositoryInterface",
    "SeverityService",
]


def __getattr__(name):
    if name == "SeverityEntity":
        from .entities import SeverityEntity
        return SeverityEntity
    if name == "SeverityRepositoryInterface":
        from .repositories import SeverityRepositoryInterface
        return SeverityRepositoryInterface
    if name == "SeverityService":
        from .services import SeverityService
        return SeverityService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
