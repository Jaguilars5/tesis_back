__all__ = [
    "IncidentType",
    "IncidentTypeRepository",
    "IncidentTypeService",
]

def __getattr__(name):
    if name == "IncidentType":
        from .infrastructure.models import IncidentType
        return IncidentType
    if name == "IncidentTypeRepository":
        from .infrastructure.repositories import IncidentTypeRepository
        return IncidentTypeRepository
    if name == "IncidentTypeService":
        from .domain.services import IncidentTypeService
        return IncidentTypeService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
