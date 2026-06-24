__all__ = [
    "TeacherSubjectSection",
    "TeacherSubjectSectionRepository",
    "TeacherSubjectSectionService",
]


def __getattr__(name):
    if name == "TeacherSubjectSection":
        from .infrastructure.models import TeacherSubjectSection
        return TeacherSubjectSection
    if name == "TeacherSubjectSectionRepository":
        from .infrastructure.repositories import TeacherSubjectSectionRepository
        return TeacherSubjectSectionRepository
    if name == "TeacherSubjectSectionService":
        from .domain.services import TeacherSubjectSectionService
        return TeacherSubjectSectionService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
