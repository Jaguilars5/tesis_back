__all__ = [
    "Section",
    "SectionRepository",
    "SectionService",
]

def __getattr__(name):
    if name == "Section":
        from .infrastructure.models import Section
        return Section
    if name == "SectionRepository":
        from .infrastructure.repositories import SectionRepository
        return SectionRepository
    if name == "SectionService":
        from .domain.services import SectionService
        return SectionService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
