__all__ = ["Subject", "SubjectRepository"]


def __getattr__(name):
    if name == "Subject":
        from .models import Subject
        return Subject
    if name == "SubjectRepository":
        from .repositories import SubjectRepository
        return SubjectRepository
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
