"""Capa de dominio del bounded context attendance_core."""

__all__ = [
    "AttendanceEntity",
    "AttendanceRepositoryInterface",
    "AttendanceService",
]


def __getattr__(name):
    if name == "AttendanceEntity":
        from .entities import AttendanceEntity
        return AttendanceEntity
    if name == "AttendanceRepositoryInterface":
        from .repositories import AttendanceRepositoryInterface
        return AttendanceRepositoryInterface
    if name == "AttendanceService":
        from .services import AttendanceService
        return AttendanceService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
