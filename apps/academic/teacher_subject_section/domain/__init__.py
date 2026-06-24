__all__ = [
    "TeacherSubjectSectionEntity",
    "TeacherSubjectSectionRepositoryInterface",
    "TeacherSubjectSectionService",
]


def __getattr__(name):
    if name == "TeacherSubjectSectionEntity":
        from .entities import TeacherSubjectSectionEntity
        return TeacherSubjectSectionEntity
    if name == "TeacherSubjectSectionRepositoryInterface":
        from .repositories import TeacherSubjectSectionRepositoryInterface
        return TeacherSubjectSectionRepositoryInterface
    if name == "TeacherSubjectSectionService":
        from .services import TeacherSubjectSectionService
        return TeacherSubjectSectionService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
