__all__ = ["SubjectOfferingViewSet"]


def __getattr__(name):
    if name == "SubjectOfferingViewSet":
        from .views import SubjectOfferingViewSet
        return SubjectOfferingViewSet
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
