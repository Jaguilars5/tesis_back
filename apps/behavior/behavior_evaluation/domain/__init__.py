"""Capa de dominio del bounded context behavior_evaluation."""

__all__ = [
    "BehaviorEvaluationEntity",
    "BehaviorEvaluationRepositoryInterface",
    "BehaviorEvaluationService",
]


def __getattr__(name):
    if name == "BehaviorEvaluationEntity":
        from .entities import BehaviorEvaluationEntity
        return BehaviorEvaluationEntity
    if name == "BehaviorEvaluationRepositoryInterface":
        from .repositories import BehaviorEvaluationRepositoryInterface
        return BehaviorEvaluationRepositoryInterface
    if name == "BehaviorEvaluationService":
        from .services import BehaviorEvaluationService
        return BehaviorEvaluationService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
