__all__ = [
    "SubjectOffering",
    "SubjectOfferingRepository",
    "SubjectOfferingService",
]


def __getattr__(name):
    if name == "SubjectOffering":
        from .infrastructure.models import SubjectOffering
        return SubjectOffering
    if name == "SubjectOfferingRepository":
        from .infrastructure.repositories import SubjectOfferingRepository
        return SubjectOfferingRepository
    if name == "SubjectOfferingService":
        from .domain.services import SubjectOfferingService
        return SubjectOfferingService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
