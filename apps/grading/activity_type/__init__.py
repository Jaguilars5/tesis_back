__all__ = [
    "ActivityType",
    "ActivityTypeRepository",
    "ActivityTypeService",
]

def __getattr__(name):
    if name == "ActivityType":
        from .infrastructure.models import ActivityType
        return ActivityType
    if name == "ActivityTypeRepository":
        from .infrastructure.repositories import ActivityTypeRepository
        return ActivityTypeRepository
    if name == "ActivityTypeService":
        from .domain.services import ActivityTypeService
        return ActivityTypeService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
