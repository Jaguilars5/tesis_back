__all__ = ["TeacherSubjectSection", "TeacherSubjectSectionRepository"]


def __getattr__(name):
    if name == "TeacherSubjectSection":
        from .models import TeacherSubjectSection
        return TeacherSubjectSection
    if name == "TeacherSubjectSectionRepository":
        from .repositories import TeacherSubjectSectionRepository
        return TeacherSubjectSectionRepository
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
