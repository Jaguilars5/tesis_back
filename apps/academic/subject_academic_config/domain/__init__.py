__all__ = [
    "SubjectAcademicConfigRepositoryInterface",
    "SubjectAcademicConfigService",
]


def __getattr__(name):
    if name == "SubjectAcademicConfigRepositoryInterface":
        from .repositories import SubjectAcademicConfigRepositoryInterface
        return SubjectAcademicConfigRepositoryInterface
    if name == "SubjectAcademicConfigService":
        from .services import SubjectAcademicConfigService
        return SubjectAcademicConfigService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
