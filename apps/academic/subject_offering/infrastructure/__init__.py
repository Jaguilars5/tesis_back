__all__ = ["SubjectOffering", "SubjectOfferingRepository"]


def __getattr__(name):
    if name == "SubjectOffering":
        from .models import SubjectOffering
        return SubjectOffering
    if name == "SubjectOfferingRepository":
        from .repositories import SubjectOfferingRepository
        return SubjectOfferingRepository
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
