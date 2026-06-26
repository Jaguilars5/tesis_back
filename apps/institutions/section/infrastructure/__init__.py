__all__ = ["Section", "SectionRepository"]


def __getattr__(name):
    if name == "Section":
        from .models import Section
        return Section
    if name == "SectionRepository":
        from .repositories import SectionRepository
        return SectionRepository
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
