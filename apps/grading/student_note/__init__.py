__all__ = [
    "StudentNote",
    "GradeChangeHistory",
    "PeriodGradeSummary",
    "StudentNoteRepository",
    "PeriodGradeSummaryRepository",
    "StudentNoteService",
    "GradeCalculationService",
]

def __getattr__(name):
    if name == "StudentNote":
        from .infrastructure.models import StudentNote
        return StudentNote
    if name == "GradeChangeHistory":
        from .infrastructure.models import GradeChangeHistory
        return GradeChangeHistory
    if name == "PeriodGradeSummary":
        from .infrastructure.models import PeriodGradeSummary
        return PeriodGradeSummary
    if name == "StudentNoteRepository":
        from .infrastructure.repositories import StudentNoteRepository
        return StudentNoteRepository
    if name == "PeriodGradeSummaryRepository":
        from .infrastructure.repositories import PeriodGradeSummaryRepository
        return PeriodGradeSummaryRepository
    if name == "StudentNoteService":
        from .domain.services import StudentNoteService
        return StudentNoteService
    if name == "GradeCalculationService":
        from .domain.services import GradeCalculationService
        return GradeCalculationService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
