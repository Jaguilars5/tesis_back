__all__ = [
    "EvaluationBlock",
    "BlockComponent",
    "EvaluativeActivity",
    "EvaluationBlockRepository",
    "BlockComponentRepository",
    "EvaluativeActivityRepository",
    "EvaluationService",
]

def __getattr__(name):
    if name == "EvaluationBlock":
        from .infrastructure.models import EvaluationBlock
        return EvaluationBlock
    if name == "BlockComponent":
        from .infrastructure.models import BlockComponent
        return BlockComponent
    if name == "EvaluativeActivity":
        from .infrastructure.models import EvaluativeActivity
        return EvaluativeActivity
    if name == "EvaluationBlockRepository":
        from .infrastructure.repositories import EvaluationBlockRepository
        return EvaluationBlockRepository
    if name == "BlockComponentRepository":
        from .infrastructure.repositories import BlockComponentRepository
        return BlockComponentRepository
    if name == "EvaluativeActivityRepository":
        from .infrastructure.repositories import EvaluativeActivityRepository
        return EvaluativeActivityRepository
    if name == "EvaluationService":
        from .domain.services import EvaluationService
        return EvaluationService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
