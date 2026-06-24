__all__ = [
    "Subject",
    "SubjectRepository",
    "SubjectService",
]


def __getattr__(name):
    if name == "Subject":
        from .infrastructure.models import Subject
        return Subject
    if name == "SubjectRepository":
        from .infrastructure.repositories import SubjectRepository
        return SubjectRepository
    if name == "SubjectService":
        from .domain.services import SubjectService
        return SubjectService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
