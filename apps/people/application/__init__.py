__all__ = [
    "CitySerializer",
    "DocumentTypeSerializer",
    "PersonSerializer",
    "run_all_validators_city",
    "run_all_validators_document_type",
    "run_all_validators_person",
]


def __getattr__(name):
    if name in ("CitySerializer", "DocumentTypeSerializer", "PersonSerializer"):
        from .serializers import CitySerializer, DocumentTypeSerializer, PersonSerializer
        return {
            "CitySerializer": CitySerializer,
            "DocumentTypeSerializer": DocumentTypeSerializer,
            "PersonSerializer": PersonSerializer,
        }[name]
    if name == "run_all_validators_city":
        from .validators import run_all_validators_city
        return run_all_validators_city
    if name == "run_all_validators_document_type":
        from .validators import run_all_validators_document_type
        return run_all_validators_document_type
    if name == "run_all_validators_person":
        from .validators import run_all_validators_person
        return run_all_validators_person
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
