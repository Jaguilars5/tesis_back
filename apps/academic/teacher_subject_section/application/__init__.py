__all__ = ["TeacherSubjectSectionSerializer", "run_all_validators"]


def __getattr__(name):
    if name == "TeacherSubjectSectionSerializer":
        from .serializers import TeacherSubjectSectionSerializer
        return TeacherSubjectSectionSerializer
    if name == "run_all_validators":
        from .validators import run_all_validators
        return run_all_validators
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
