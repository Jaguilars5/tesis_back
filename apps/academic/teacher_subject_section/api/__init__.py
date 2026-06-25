__all__ = ["TeacherSubjectSectionViewSet"]


def __getattr__(name):
    if name == "TeacherSubjectSectionViewSet":
        from .views import TeacherSubjectSectionViewSet
        return TeacherSubjectSectionViewSet
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
