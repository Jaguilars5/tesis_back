__all__ = [
    "CityRepositoryInterface",
    "DocumentTypeRepositoryInterface",
    "PersonRepositoryInterface",
    "CityService",
    "DocumentTypeService",
    "PersonService",
]


def __getattr__(name):
    if name == "CityRepositoryInterface":
        from .repositories import CityRepositoryInterface
        return CityRepositoryInterface
    if name == "DocumentTypeRepositoryInterface":
        from .repositories import DocumentTypeRepositoryInterface
        return DocumentTypeRepositoryInterface
    if name == "PersonRepositoryInterface":
        from .repositories import PersonRepositoryInterface
        return PersonRepositoryInterface
    if name == "CityService":
        from .services import CityService
        return CityService
    if name == "DocumentTypeService":
        from .services import DocumentTypeService
        return DocumentTypeService
    if name == "PersonService":
        from .services import PersonService
        return PersonService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
