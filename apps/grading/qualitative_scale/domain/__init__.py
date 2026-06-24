"""Capa de dominio del bounded context qualitative_scale."""

__all__ = [
    "QualitativeScaleEntity",
    "QualitativeScaleRepositoryInterface",
    "QualitativeScaleService",
]


def __getattr__(name):
    if name == "QualitativeScaleEntity":
        from .entities import QualitativeScaleEntity
        return QualitativeScaleEntity
    if name == "QualitativeScaleRepositoryInterface":
        from .repositories import QualitativeScaleRepositoryInterface
        return QualitativeScaleRepositoryInterface
    if name == "QualitativeScaleService":
        from .services import QualitativeScaleService
        return QualitativeScaleService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
