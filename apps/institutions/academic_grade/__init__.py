__all__ = [
    "AcademicGrade",
    "AcademicGradeRepository",
    "AcademicGradeService",
]


def __getattr__(name):
    if name == "AcademicGrade":
        from .infrastructure.models import AcademicGrade
        return AcademicGrade
    if name == "AcademicGradeRepository":
        from .infrastructure.repositories import AcademicGradeRepository
        return AcademicGradeRepository
    if name == "AcademicGradeService":
        from .domain.services import AcademicGradeService
        return AcademicGradeService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
