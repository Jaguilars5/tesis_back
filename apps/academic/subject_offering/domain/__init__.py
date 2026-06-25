__all__ = [
    "SubjectOfferingRepositoryInterface",
    "SubjectOfferingService",
]


def __getattr__(name):
    if name == "SubjectOfferingRepositoryInterface":
        from .repositories import SubjectOfferingRepositoryInterface
        return SubjectOfferingRepositoryInterface
    if name == "SubjectOfferingService":
        from .services import SubjectOfferingService
        return SubjectOfferingService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
