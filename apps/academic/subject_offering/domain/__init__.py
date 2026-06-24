__all__ = [
    "SubjectOfferingEntity",
    "SubjectOfferingRepositoryInterface",
    "SubjectOfferingService",
]


def __getattr__(name):
    if name == "SubjectOfferingEntity":
        from .entities import SubjectOfferingEntity
        return SubjectOfferingEntity
    if name == "SubjectOfferingRepositoryInterface":
        from .repositories import SubjectOfferingRepositoryInterface
        return SubjectOfferingRepositoryInterface
    if name == "SubjectOfferingService":
        from .services import SubjectOfferingService
        return SubjectOfferingService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
