__all__ = [
    "ConductIncident",
    "ConductIncidentRepository",
    "ConductIncidentService",
]

def __getattr__(name):
    if name == "ConductIncident":
        from .infrastructure.models import ConductIncident
        return ConductIncident
    if name == "ConductIncidentRepository":
        from .infrastructure.repositories import ConductIncidentRepository
        return ConductIncidentRepository
    if name == "ConductIncidentService":
        from .domain.services import ConductIncidentService
        return ConductIncidentService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
