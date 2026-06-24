"""Capa de dominio del bounded context absence_type."""

__all__ = [
    "AbsenceTypeEntity",
    "AbsenceTypeRepositoryInterface",
    "AbsenceTypeService",
]


def __getattr__(name):
    if name == "AbsenceTypeEntity":
        from .entities import AbsenceTypeEntity
        return AbsenceTypeEntity
    if name == "AbsenceTypeRepositoryInterface":
        from .repositories import AbsenceTypeRepositoryInterface
        return AbsenceTypeRepositoryInterface
    if name == "AbsenceTypeService":
        from .services import AbsenceTypeService
        return AbsenceTypeService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
