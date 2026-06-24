__all__ = [
    "AcademicGradeEntity",
    "AcademicGradeRepositoryInterface",
    "AcademicGradeService",
]


def __getattr__(name):
    if name == "AcademicGradeEntity":
        from .entities import AcademicGradeEntity
        return AcademicGradeEntity
    if name == "AcademicGradeRepositoryInterface":
        from .repositories import AcademicGradeRepositoryInterface
        return AcademicGradeRepositoryInterface
    if name == "AcademicGradeService":
        from .services import AcademicGradeService
        return AcademicGradeService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
