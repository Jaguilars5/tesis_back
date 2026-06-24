"""Capa de dominio del bounded context activity_type."""

__all__ = [
    "ActivityTypeEntity",
    "ActivityTypeRepositoryInterface",
    "ActivityTypeService",
]


def __getattr__(name):
    if name == "ActivityTypeEntity":
        from .entities import ActivityTypeEntity
        return ActivityTypeEntity
    if name == "ActivityTypeRepositoryInterface":
        from .repositories import ActivityTypeRepositoryInterface
        return ActivityTypeRepositoryInterface
    if name == "ActivityTypeService":
        from .services import ActivityTypeService
        return ActivityTypeService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
