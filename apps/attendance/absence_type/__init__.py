__all__ = [
    "AbsenceType",
    "AbsenceTypeRepository",
    "AbsenceTypeService",
]

def __getattr__(name):
    if name == "AbsenceType":
        from .infrastructure.models import AbsenceType
        return AbsenceType
    if name == "AbsenceTypeRepository":
        from .infrastructure.repositories import AbsenceTypeRepository
        return AbsenceTypeRepository
    if name == "AbsenceTypeService":
        from .domain.services import AbsenceTypeService
        return AbsenceTypeService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
