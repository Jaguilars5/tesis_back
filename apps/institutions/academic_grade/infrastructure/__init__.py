__all__ = ["AcademicGrade", "AcademicGradeRepository"]


def __getattr__(name):
    if name == "AcademicGrade":
        from .models import AcademicGrade
        return AcademicGrade
    if name == "AcademicGradeRepository":
        from .repositories import AcademicGradeRepository
        return AcademicGradeRepository
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
