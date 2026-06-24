"""Capa de dominio del bounded context conduct_incident."""

__all__ = [
    "ConductIncidentEntity",
    "ConductIncidentRepositoryInterface",
    "ConductIncidentService",
]


def __getattr__(name):
    if name == "ConductIncidentEntity":
        from .entities import ConductIncidentEntity
        return ConductIncidentEntity
    if name == "ConductIncidentRepositoryInterface":
        from .repositories import ConductIncidentRepositoryInterface
        return ConductIncidentRepositoryInterface
    if name == "ConductIncidentService":
        from .services import ConductIncidentService
        return ConductIncidentService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
