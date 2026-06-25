__all__ = ["SubjectOfferingSerializer", "run_all_validators"]


def __getattr__(name):
    if name == "SubjectOfferingSerializer":
        from .serializers import SubjectOfferingSerializer
        return SubjectOfferingSerializer
    if name == "run_all_validators":
        from .validators import run_all_validators
        return run_all_validators
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
