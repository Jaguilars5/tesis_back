"""Capa de dominio del bounded context section."""

__all__ = [
    "SectionEntity",
    "SectionRepositoryInterface",
    "SectionService",
]


def __getattr__(name):
    if name == "SectionEntity":
        from .entities import SectionEntity
        return SectionEntity
    if name == "SectionRepositoryInterface":
        from .repositories import SectionRepositoryInterface
        return SectionRepositoryInterface
    if name == "SectionService":
        from .services import SectionService
        return SectionService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
