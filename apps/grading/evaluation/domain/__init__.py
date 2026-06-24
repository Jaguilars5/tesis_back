"""Capa de dominio del bounded context evaluation."""

__all__ = [
    "EvaluationBlockEntity",
    "BlockComponentEntity",
    "EvaluativeActivityEntity",
    "EvaluationService",
]


def __getattr__(name):
    if name == "EvaluationBlockEntity":
        from .entities import EvaluationBlockEntity
        return EvaluationBlockEntity
    if name == "BlockComponentEntity":
        from .entities import BlockComponentEntity
        return BlockComponentEntity
    if name == "EvaluativeActivityEntity":
        from .entities import EvaluativeActivityEntity
        return EvaluativeActivityEntity
    if name == "EvaluationService":
        from .services import EvaluationService
        return EvaluationService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
