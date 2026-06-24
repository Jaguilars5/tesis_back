__all__ = [
    "SubjectEntity",
    "SubjectRepositoryInterface",
    "SubjectService",
]


def __getattr__(name):
    if name == "SubjectEntity":
        from .entities import SubjectEntity
        return SubjectEntity
    if name == "SubjectRepositoryInterface":
        from .repositories import SubjectRepositoryInterface
        return SubjectRepositoryInterface
    if name == "SubjectService":
        from .services import SubjectService
        return SubjectService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
