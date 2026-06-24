__all__ = [
    "AttendanceStatus",
    "AttendanceStatusRepository",
    "AttendanceStatusService",
]

def __getattr__(name):
    if name == "AttendanceStatus":
        from .infrastructure.models import AttendanceStatus
        return AttendanceStatus
    if name == "AttendanceStatusRepository":
        from .infrastructure.repositories import AttendanceStatusRepository
        return AttendanceStatusRepository
    if name == "AttendanceStatusService":
        from .domain.services import AttendanceStatusService
        return AttendanceStatusService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
