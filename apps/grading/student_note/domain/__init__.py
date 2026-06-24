"""Capa de dominio del bounded context student_note."""

__all__ = [
    "StudentNoteEntity",
    "GradeChangeHistoryEntity",
    "PeriodGradeSummaryEntity",
    "StudentNoteService",
    "GradeCalculationService",
]


def __getattr__(name):
    if name == "StudentNoteEntity":
        from .entities import StudentNoteEntity
        return StudentNoteEntity
    if name == "GradeChangeHistoryEntity":
        from .entities import GradeChangeHistoryEntity
        return GradeChangeHistoryEntity
    if name == "PeriodGradeSummaryEntity":
        from .entities import PeriodGradeSummaryEntity
        return PeriodGradeSummaryEntity
    if name == "StudentNoteService":
        from .services import StudentNoteService
        return StudentNoteService
    if name == "GradeCalculationService":
        from .services import GradeCalculationService
        return GradeCalculationService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
