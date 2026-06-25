__all__ = ["SubjectAcademicConfigSerializer", "run_all_validators"]


def __getattr__(name):
    if name == "SubjectAcademicConfigSerializer":
        from .serializers import SubjectAcademicConfigSerializer
        return SubjectAcademicConfigSerializer
    if name == "run_all_validators":
        from .validators import run_all_validators
        return run_all_validators
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
