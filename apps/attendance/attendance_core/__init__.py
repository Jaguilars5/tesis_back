__all__ = [
    "Attendance",
    "AttendanceRepository",
    "AttendanceService",
]

def __getattr__(name):
    if name == "Attendance":
        from .infrastructure.models import Attendance
        return Attendance
    if name == "AttendanceRepository":
        from .infrastructure.repositories import AttendanceRepository
        return AttendanceRepository
    if name == "AttendanceService":
        from .domain.services import AttendanceService
        return AttendanceService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
