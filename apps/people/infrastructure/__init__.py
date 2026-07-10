__all__ = ["City", "DocumentType", "Person", "CityRepository", "DocumentTypeRepository", "PersonRepository"]


def __getattr__(name):
    if name == "City":
        from .models import City
        return City
    if name == "DocumentType":
        from .models import DocumentType
        return DocumentType
    if name == "Person":
        from .models import Person
        return Person
    if name == "CityRepository":
        from .repositories import CityRepository
        return CityRepository
    if name == "DocumentTypeRepository":
        from .repositories import DocumentTypeRepository
        return DocumentTypeRepository
    if name == "PersonRepository":
        from .repositories import PersonRepository
        return PersonRepository
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
