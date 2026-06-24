__all__ = [
    "SubjectAcademicConfig",
    "SubjectAcademicConfigRepository",
    "SubjectAcademicConfigService",
]


def __getattr__(name):
    if name == "SubjectAcademicConfig":
        from .infrastructure.models import SubjectAcademicConfig
        return SubjectAcademicConfig
    if name == "SubjectAcademicConfigRepository":
        from .infrastructure.repositories import SubjectAcademicConfigRepository
        return SubjectAcademicConfigRepository
    if name == "SubjectAcademicConfigService":
        from .domain.services import SubjectAcademicConfigService
        return SubjectAcademicConfigService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
