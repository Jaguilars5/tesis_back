__all__ = [
    "QualitativeScale",
    "QualitativeScaleSublevel",
    "QualitativeScaleRepository",
    "QualitativeScaleService",
]

def __getattr__(name):
    if name == "QualitativeScale":
        from .infrastructure.models import QualitativeScale
        return QualitativeScale
    if name == "QualitativeScaleSublevel":
        from .infrastructure.models import QualitativeScaleSublevel
        return QualitativeScaleSublevel
    if name == "QualitativeScaleRepository":
        from .infrastructure.repositories import QualitativeScaleRepository
        return QualitativeScaleRepository
    if name == "QualitativeScaleService":
        from .domain.services import QualitativeScaleService
        return QualitativeScaleService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
