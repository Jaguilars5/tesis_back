__all__ = [
    "BehaviorEvaluation",
    "BehaviorEvaluationRepository",
    "BehaviorEvaluationService",
]

def __getattr__(name):
    if name == "BehaviorEvaluation":
        from .infrastructure.models import BehaviorEvaluation
        return BehaviorEvaluation
    if name == "BehaviorEvaluationRepository":
        from .infrastructure.repositories import BehaviorEvaluationRepository
        return BehaviorEvaluationRepository
    if name == "BehaviorEvaluationService":
        from .domain.services import BehaviorEvaluationService
        return BehaviorEvaluationService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
