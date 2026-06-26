__all__ = [
    "SyncQueue",
    "SyncableModel",
    "SyncStatusChoices",
    "SyncOperationChoices",
    "SyncQueueRepository",
    "SyncQueueService",
    "ConflictResolutionStrategy",
    "SyncQueueSerializer",
    "SyncQueueViewSet",
]


def __getattr__(name):
    if name == "SyncQueue":
        from .infrastructure.models import SyncQueue
        return SyncQueue
    if name == "SyncableModel":
        from .infrastructure.models import SyncableModel
        return SyncableModel
    if name == "SyncStatusChoices":
        from .infrastructure.models import SyncStatusChoices
        return SyncStatusChoices
    if name == "SyncOperationChoices":
        from .infrastructure.models import SyncOperationChoices
        return SyncOperationChoices
    if name == "SyncQueueRepository":
        from .infrastructure.repositories import SyncQueueRepository
        return SyncQueueRepository
    if name == "SyncQueueService":
        from .domain.services import SyncQueueService
        return SyncQueueService
    if name == "ConflictResolutionStrategy":
        from .domain.services import ConflictResolutionStrategy
        return ConflictResolutionStrategy
    if name == "SyncQueueSerializer":
        from .application.serializers import SyncQueueSerializer
        return SyncQueueSerializer
    if name == "SyncQueueViewSet":
        from .api.views import SyncQueueViewSet
        return SyncQueueViewSet
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
