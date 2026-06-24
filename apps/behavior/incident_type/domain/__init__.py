"""Capa de dominio del bounded context incident_type."""

__all__ = [
    "IncidentTypeEntity",
    "IncidentTypeRepositoryInterface",
    "IncidentTypeService",
]


def __getattr__(name):
    if name == "IncidentTypeEntity":
        from .entities import IncidentTypeEntity
        return IncidentTypeEntity
    if name == "IncidentTypeRepositoryInterface":
        from .repositories import IncidentTypeRepositoryInterface
        return IncidentTypeRepositoryInterface
    if name == "IncidentTypeService":
        from .services import IncidentTypeService
        return IncidentTypeService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
