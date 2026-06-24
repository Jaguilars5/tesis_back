"""Capa de dominio del bounded context attendance_status."""

__all__ = [
    "AttendanceStatusEntity",
    "AttendanceStatusRepositoryInterface",
    "AttendanceStatusService",
]


def __getattr__(name):
    if name == "AttendanceStatusEntity":
        from .entities import AttendanceStatusEntity
        return AttendanceStatusEntity
    if name == "AttendanceStatusRepositoryInterface":
        from .repositories import AttendanceStatusRepositoryInterface
        return AttendanceStatusRepositoryInterface
    if name == "AttendanceStatusService":
        from .services import AttendanceStatusService
        return AttendanceStatusService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
